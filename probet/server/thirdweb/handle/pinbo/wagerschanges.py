import asyncio
from sqlalchemy.exc import IntegrityError
from lib.timehelp import timeHelp
import logging
import json
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from logic.logicmgr import levelCalc
from gmweb.utils.models import Base

tbl = Base.metadata.tables["dj_pinbo_wagers"]

@asyncio.coroutine
def handleHttp(bytesParam: dict):

    dictParam = json.loads(bytesParam)
    listNewBetOrder = []
    listUpdateBetOrder = []
    listSettleBetOrder = []
    listMessageData = dictParam["messageData"]

    for var_message in listMessageData:
        #先判断状态
        if var_message["loginId"] == "PSZ40":
            logging.info("agent PSZ40")
            continue
        #日志
        dictBill = {}
        dictBill['billType']='pingboBetResultBill'
        dictBill.update(var_message)
        strAccount = var_message["loginId"][7:]

        objPlayerData= yield from classDataBaseMgr.getInstance().getPlayerData(strAccount)
        if objPlayerData is None:
            logging.error("[{}] accountId is null".format(strAccount))
            dictBill['agentId'] = ""
        else:
            dictBill['agentId'] = objPlayerData.strAgentId
        logging.getLogger('bill').info(json.dumps(dictBill))

        if var_message["status"] == "OPEN" or var_message["status"] == "PENDING":
            # 投注
            listNewBetOrder.append(var_message)
        elif var_message["status"] == "SETTLED":
            listSettleBetOrder.append(var_message)
        else:
            #CANCELLED DELETED
            listUpdateBetOrder.append(var_message)

    #纪录需要及时计算流水信息
    #listSet = []
    for var_message in listSettleBetOrder:
        strAccount = var_message["loginId"][7:]
        #todo bill
        with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
            is_exist_sql = "select * from dj_pinbo_wagers WHERE wagerId=%s "
            is_exist = yield from conn.execute(is_exist_sql, [var_message['wagerId']])
            is_exist = yield from is_exist.fetchone()
            if is_exist.status != 'SETTLED' and var_message['status'] == 'SETTLED':
                objPlayerData, objPlayerLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccount)
                if objPlayerData is None:
                    logging.error("accountId[{}] not valid".format(strAccount))
                else:
                    # 不可提现额度减投注额，直到0为止
                    if objPlayerData.iNotDrawingCoin - var_message['toRisk'] * 100 < 0:
                        objPlayerData.iNotDrawingCoin = 0
                    else:
                        objPlayerData.iNotDrawingCoin -= int(var_message['toRisk'] * 100)
                    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerLock)

        #listSet.append(var_message["loginId"])
        #yield from classDataBaseMgr.getInstance().setCalcWaterPinboAccountId(listSet)
        #判断是否是有效流水

        if var_message["odds"] >= 1.50:
            objPlayerData,objPlayerLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccount)
            if objPlayerData is None:
                logging.error("accountId[{}] not valid".format(strAccount))
                continue
            #及时计算vip等级和有效流水金额
            objPlayerData.iLevel,objPlayerData.iLevelValidWater = levelCalc.calPlayerVipLevel(objPlayerData.iLevel, objPlayerData.iLevelValidWater, var_message["toRisk"] * 100)

            yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData,objPlayerLock)


    engine = classSqlBaseMgr.getInstance().getEngine()

    with (yield from engine) as conn:
        yield from addNewBetOrder(listNewBetOrder,conn)
        yield from updateBetOrder(listUpdateBetOrder,conn)
        #todo replace语法优化   REPLACE INTO users (id,name,age) VALUES(123, ‘chao’, 50);
        yield from updateBetOrder(listSettleBetOrder,conn)

    #查阅示例代码，要返回这个messageid
    return str(dictParam["messageId"]).encode()

@asyncio.coroutine
def updateBetOrder(messageDataList:list,conn):
    accountIds=set()
    for var_message in messageDataList:
        if var_message['status']=='SETTLED':
            accountIds.add(var_message['loginId'][7:])

        sql = tbl.update().where(tbl.c.wagerId==var_message["wagerId"]).values(
            oddsFormat=var_message["oddsFormat"], #滚球
            odds=var_message["odds"],
            stake=var_message["stake"],
            toWin=var_message["toWin"],
            toRisk=var_message["toRisk"],
            winLoss=var_message["winLoss"],
            currencyCode=var_message["currencyCode"],
            status=var_message["status"],
            loginId=var_message["loginId"],
            wagerDateFm= timeHelp.strToTimestamp(var_message["wagerDateFm"]),
            settleDateFm=0 if var_message["settleDateFm"] is None else timeHelp.strToTimestamp(var_message["settleDateFm"]),
            messageData=json.dumps(var_message),
        )
        trans = yield from conn.begin()
        try:
            for accountId in accountIds:
                yield from classDataBaseMgr.getInstance().addUpdatePingboAccountId(accountId)
            yield from conn.execute(sql)
        except IntegrityError as e :
            #如果主键重复则更新数据
            logging.debug(repr(e))
            yield from updateBetOrder([var_message])
            yield from trans.commit()
            continue
        except Exception as e:
            logging.error(e)
            logging.error(var_message)
            yield from trans.rollback()
            continue
        else:
            yield from trans.commit()


@asyncio.coroutine
def addNewBetOrder(messageDataList:list,conn):

    for var_message in messageDataList:

        sql = tbl.insert().values(
            wagerId=var_message["wagerId"],
            oddsFormat=var_message["oddsFormat"],
            odds=var_message["odds"],
            stake=var_message["stake"],
            toWin=var_message["toWin"],
            toRisk=var_message["toRisk"],
            winLoss=var_message["winLoss"],
            currencyCode=var_message["currencyCode"],
            status=var_message["status"],
            loginId=var_message["loginId"],
            wagerDateFm= timeHelp.strToTimestamp(var_message["wagerDateFm"]),
            settleDateFm=0 if var_message["settleDateFm"] is None else timeHelp.strToTimestamp(
                var_message["settleDateFm"]),
            messageData=json.dumps(var_message),
        )

        trans = yield from conn.begin()
        try:
            yield from conn.execute(sql)
        except IntegrityError as e:
            #主键重复，更新一遍
            logging.debug(repr(e))
            yield from trans.rollback()
            yield from updateBetOrder([var_message])
            continue
        except Exception as e:
            logging.error(e)
            yield from trans.rollback()
            continue
        else:
            yield from trans.commit()


def getPinboHistoryValidWater():
    sql_eu = "select sum(dj_pinbo_wagers.toRisk) as validWaterCoin from dj_pinbo_wagers where dj_pinbo_wagers.loginId =CONCAT('probet.',%s) and dj_pinbo_wagers.status = 'SETTLED' and dj_pinbo_wagers.odds >= 1.5 and oddsFormat<>0 and dj_pinbo_wagers.wagerDateFm > %s and dj_pinbo_wagers.wagerDateFm < %s"
    sql_am = "select sum(dj_pinbo_wagers.toRisk) as validWaterCoin from dj_pinbo_wagers where dj_pinbo_wagers.loginId =CONCAT('probet.',%s) and dj_pinbo_wagers.status = 'SETTLED' and ((-200 <= dj_pinbo_wagers.odds < 0) or (dj_pinbo_wagers.odds >=50)) and oddsFormat=0 and dj_pinbo_wagers.wagerDateFm > %s and dj_pinbo_wagers.wagerDateFm < %s"
    return sql_eu, sql_am

def getAllPinboHistoryValidWater():
    sql_eu = "select any_value(dj_pinbo_wagers.loginId) as loginId, sum(dj_pinbo_wagers.toRisk) as validWaterCoin from dj_pinbo_wagers where dj_pinbo_wagers.status = 'SETTLED' and dj_pinbo_wagers.odds >= 1.5 and oddsFormat<>0 and dj_pinbo_wagers.wagerDateFm > %s and dj_pinbo_wagers.wagerDateFm < %s order by dj_pinbo_wagers.loginId"
    sql_am = "select any_value(dj_pinbo_wagers.loginId) as loginId, sum(dj_pinbo_wagers.toRisk) as validWaterCoin from dj_pinbo_wagers where dj_pinbo_wagers.status = 'SETTLED' and ((-200 <= dj_pinbo_wagers.odds < 0) or (dj_pinbo_wagers.odds >=50)) and oddsFormat=0 and dj_pinbo_wagers.wagerDateFm > %s and dj_pinbo_wagers.wagerDateFm < %s order by dj_pinbo_wagers.loginId"
    return sql_eu, sql_am

def getOnePinboHistoryValidWater():
    sql_eu = "select sum(dj_pinbo_wagers.toRisk) as validWaterCoin from dj_pinbo_wagers where dj_pinbo_wagers.loginId =CONCAT('probet.',%s) and dj_pinbo_wagers.status = 'SETTLED' and dj_pinbo_wagers.odds >= 1.5 and oddsFormat<>0 and dj_pinbo_wagers.wagerDateFm > %s and dj_pinbo_wagers.wagerDateFm < %s"
    sql_am = "select sum(dj_pinbo_wagers.toRisk) as validWaterCoin from dj_pinbo_wagers where dj_pinbo_wagers.loginId =CONCAT('probet.',%s) and dj_pinbo_wagers.status = 'SETTLED' and ((-200 <= dj_pinbo_wagers.odds < 0) or (dj_pinbo_wagers.odds >=50)) and oddsFormat=0 and dj_pinbo_wagers.wagerDateFm > %s and dj_pinbo_wagers.wagerDateFm < %s"
    return sql_eu, sql_am

