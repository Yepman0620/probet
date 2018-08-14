import asyncio
from lib.jsonhelp import classJsonDump
from lib.timehelp import timeHelp
import logging
import sqlalchemy as sa
from lib.timehelp.timeHelp import strToTimestamp
import json
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from logic.logicmgr import levelCalc

from gmweb.utils.models import Base
from osssvr.utils.models import PingboBetBill

tbl = Base.metadata.tables["dj_pinbo_wagers"]
agentId=""

@asyncio.coroutine
def todo_pingbo_wagers(wagers: dict):
    conn=classSqlBaseMgr.getInstance()
    is_exist_sql="select * from dj_pinbo_wagers WHERE wagerId={} ".format(wagers['wagerId'])
    is_exist=yield from conn._exeCute(is_exist_sql)
    is_exist=yield from is_exist.fetchone()
    engine = classSqlBaseMgr.getInstance().getEngine()

    with (yield from engine) as mysql_conn:
        logging.debug(wagers)
        if is_exist is None: # 不存在新增
            # 结算了才计算不可提现额度
            if wagers['status'] == 'SETTLED':
                strAccount = wagers["loginId"][7:]
                objPlayerData, objPlayerLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccount)
                if objPlayerData is None:
                    logging.error("accountId[{}] not valid".format(strAccount))
                else:
                    # 不可提现额度减投注额，直到0为止
                    if objPlayerData.iNotDrawingCoin - wagers['toRisk']*100 < 0:
                        objPlayerData.iNotDrawingCoin = 0
                    else:
                        objPlayerData.iNotDrawingCoin -= int(wagers['toRisk']*100)
                    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerLock)
            # 判断是否是有效流水
            if wagers["odds"] >= 1.50:
                strAccount = wagers["loginId"][7:]
                objPlayerData, objPlayerLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccount)
                if objPlayerData is None:
                    logging.error("accountId[{}] not valid".format(strAccount))
                # 及时计算vip等级和有效流水金额
                else:
                    objPlayerData.iLevel, objPlayerData.iLevelValidWater = levelCalc.calPlayerVipLevel(objPlayerData.iLevel,
                                                                                                       objPlayerData.iLevelValidWater,
                                                                                                       wagers["toRisk"] * 100)
                    global agentId
                    agentId=objPlayerData.strAgentId
                    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerLock)

            dictWager={}
            dictWager['messageData']=wagers
            dictWager['wagerId']=wagers['wagerId']
            dictWager['oddsFormat']=wagers['oddsFormat']
            dictWager['odds']=wagers['odds']
            dictWager['stake']=wagers['stake']
            dictWager['toWin']=wagers['toWin']
            dictWager['toRisk']=wagers['toRisk']
            dictWager['winLoss']=wagers['winLoss']
            dictWager['currencyCode']=wagers['currencyCode']
            dictWager['loginId']=wagers['loginId']
            dictWager['wagerDateFm']=wagers['wagerDateFm']
            dictWager['status']=wagers['status']
            dictWager['settleDateFm']=wagers['settleDateFm']

            ret=yield from addNewBetOrder(dictWager, mysql_conn)

        else:
            if is_exist.status != 'SETTLED' and wagers['status'] == 'SETTLED':
                strAccount = wagers["loginId"][7:]
                objPlayerData, objPlayerLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccount)
                if objPlayerData is None:
                    logging.error("accountId[{}] not valid".format(strAccount))
                else:
                    # 不可提现额度减投注额，直到0为止
                    if objPlayerData.iNotDrawingCoin - wagers['toRisk'] * 100 < 0:
                        objPlayerData.iNotDrawingCoin = 0
                    else:
                        objPlayerData.iNotDrawingCoin -= int(wagers['toRisk'] * 100)
                    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerLock)
            # 存在修复
            ret=yield from updateBetOrder(wagers, mysql_conn)

        return ret

@asyncio.coroutine
def updateBetOrder(var_message:dict,conn):
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
            # messageData=json.dumps(var_message),
        )

        trans = yield from conn.begin()
        try:
            yield from conn.execute(sql)
        except Exception as e:
            logging.error(e)
            logging.error(var_message)
            yield from trans.rollback()
            return False,'update'
        else:
            # 日志
            dictBill = {}
            dictBill['billType'] = 'pingboBetResultBill'
            dictBill.update(var_message)
            dictBill['agentId'] = agentId
            logging.getLogger('bill').info(json.dumps(dictBill))
            yield from trans.commit()
            return True,'update'



@asyncio.coroutine
def addNewBetOrder(var_message:dict,conn):
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
        messageData=json.dumps(var_message['messageData']),
    )


    trans = yield from conn.begin()
    try:
        yield from conn.execute(sql)
    except Exception as e:
        logging.error(e)
        yield from trans.rollback()
        return False,'add'
    else:
        # 日志
        dictBill = {}
        dictBill['billType'] = 'pingboBetResultBill'
        dictBill.update(var_message)
        dictBill['agentId'] = agentId
        logging.getLogger('bill').info(json.dumps(dictBill))
        yield from trans.commit()
        return True,'add'



