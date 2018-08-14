import asyncio
import json
from datawrapper.sqlBaseMgr import classSqlBaseMgr
import logging
from error.errorCode import exceptionLogic, errorLogic
from gmweb.protocol.gmProtocol import pingboBetType
from gmweb.utils.tools import token_required, permission_required
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow,sevenDayTimestamp,strToTimestamp
import ast
class cData():
    def __init__(self):
        self.guessUId = ""
        # self.matchId = ""
        # self.matchType = ""

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('投注记录查询')
@asyncio.coroutine
def handleHttp(request: dict):
    # 根据条件查询数据库用户竞猜信息
    userId=request.get('userId','')
    phone=request.get('phone','')
    email=request.get('email','')
    # 竞猜单号
    guessUId=request.get('guessUId','')
    product=request.get('product','')
    startTime=request.get('startTime',sevenDayTimestamp())
    endTime=request.get('endTime',getNow())
    pn=request.get('pn',1)
    try:
        pn=int(pn)
    except Exception as e:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        conn = classSqlBaseMgr.getInstance()
        probet_sql=None
        pinbo_sql=None
        if guessUId:
            if product=='all':
                probet_sql="select guessUId from dj_bet WHERE guessUId='{}'".format(guessUId)
                pinbo_sql="select wagerId from dj_pinbo_wagers WHERE dj_pinbo_wagers.wagerId='{}'".format(guessUId)

            elif product=='probet':
                probet_sql = "select guessUId from dj_bet WHERE guessUId='{}'".format(guessUId)

            else:
                pinbo_sql = "select wagerId from dj_pinbo_wagers WHERE wagerId='{}'".format(guessUId)

        else:
            accountId=None
            if userId:
                sql = "select accountId from dj_account WHERE dj_account.accountId='{}' ".format(userId)
                listRest = yield from conn._exeCute(sql)
                accountId = yield from listRest.fetchone()
                if accountId is None:
                    logging.debug(errorLogic.player_data_not_found)
                    raise exceptionLogic(errorLogic.player_data_not_found)
                accountId = accountId[0]

            elif phone:
                sql="select accountId from dj_account WHERE dj_account.phone='{}' ".format(phone)
                listRest = yield from conn._exeCute(sql)
                accountId = yield from listRest.fetchone()
                if accountId is None:
                    logging.debug(errorLogic.player_data_not_found)
                    raise exceptionLogic(errorLogic.player_data_not_found)
                accountId=accountId[0]

            elif email:
                sql = "select accountId from dj_account WHERE dj_account.email='{}' ".format(email)
                listRest = yield from conn._exeCute(sql)
                accountId = yield from listRest.fetchone()
                if accountId is None:
                    logging.debug(errorLogic.player_data_not_found)
                    raise exceptionLogic(errorLogic.player_data_not_found)
                accountId=accountId[0]

            if product=='all':
                # 查全部 todo 两张不同表分页暂时没想到好的解决方案
                if not accountId:
                    probet_sql="select guessUId from dj_bet WHERE dj_bet.time BETWEEN {} AND {} ORDER BY dj_bet.time DESC ".format(startTime,endTime)
                    pinbo_sql = "select wagerId from dj_pinbo_wagers WHERE dj_pinbo_wagers.wagerDateFm BETWEEN {} AND {} ORDER BY wagerDateFm DESC ".format(
                        startTime, endTime)
                else:
                    probet_sql = "select guessUId from dj_bet WHERE dj_bet.accountId='{}' AND dj_bet.time BETWEEN {} AND {} ORDER BY dj_bet.time DESC ".format(accountId,startTime,endTime)

                    pinbo_sql = "select wagerId from dj_pinbo_wagers WHERE dj_pinbo_wagers.loginId='{}' AND dj_pinbo_wagers.wagerDateFm BETWEEN {} AND {} ORDER BY wagerDateFm DESC ".format(
                        'probet.'+accountId,startTime,endTime)

            elif product=='probet':
                #查自己平台
                if not accountId:
                    probet_sql = "select guessUId from dj_bet WHERE dj_bet.time BETWEEN {} AND {} ORDER BY dj_bet.time DESC ".format(startTime, endTime)
                else:
                    probet_sql = "select guessUId from dj_bet WHERE dj_bet.accountId='{}' AND dj_bet.time BETWEEN {} AND {} ORDER BY wagerDateFm DESC ".format(
                        accountId, startTime, endTime)

            else:
                #查平博
                if not accountId:
                    pinbo_sql = "select wagerId from dj_pinbo_wagers WHERE dj_pinbo_wagers.wagerDateFm BETWEEN {} AND {} ORDER BY wagerDateFm DESC ".format(startTime, endTime)
                else:
                    pinbo_sql = "select wagerId from dj_pinbo_wagers WHERE dj_pinbo_wagers.loginId='{}' AND dj_pinbo_wagers.wagerDateFm BETWEEN {} AND {} ORDER BY wagerDateFm DESC ".format(
                        'probet.' + accountId, startTime, endTime)

        probet_bets = []
        pinbo_bets = []
        probet_betids=None
        pinbo_betids=None
        if probet_sql is not None:
            listRest = yield from conn._exeCute(probet_sql)
            probet_betids = yield from listRest.fetchall()

        if pinbo_sql is not None:
            listRest = yield from conn._exeCute(pinbo_sql)
            pinbo_betids = yield from listRest.fetchall()

        if probet_betids is not None:
            for x in probet_betids:
                probet_bets.append({"probet":x[0]})
        if pinbo_betids is not None:
            for x in pinbo_betids:
                pinbo_bets.append({"pingbo":x[0]})

        probet_bets.extend(pinbo_bets)
        count=len(probet_bets)
        betids=probet_bets[(pn-1)*MSG_PAGE_COUNT:pn*MSG_PAGE_COUNT:]
        resp=cResp()
        for x in betids:
            if "probet" in x.keys():
                sql="select * from dj_bet WHERE guessUId='{}' ".format(x['probet'])
                listRest=yield from conn._exeCute(sql)
                probet_row=yield from listRest.fetchone()
                data = cData()
                data.orders = probet_row['guessUId']
                data.accountId = probet_row['accountId']
                data.product = '电竞竞猜'
                data.time = probet_row['time']
                data.game = probet_row['matchType']
                sql="select teamAName,teamBName from dj_match WHERE matchId='{}' ".format(probet_row['matchId'])
                listRest=yield from conn._exeCute(sql)
                match=yield from listRest.fetchone()
                data.msg = "{} vs {}".format(match['teamAName'],match['teamBName'])
                ctr=json.loads(probet_row['ctr'])
                data.content = "{}/{}@{}".format(ctr[probet_row['chooseId']]['strChooseName'],probet_row['guessName'],ctr[probet_row['chooseId']]['fRate'])
                data.money = float("%.2f" % round(probet_row['betCoin'] / 100, 2))
                data.winning = float("%.2f" % round(probet_row['winCoin'] / 100, 2))
                data.status = probet_row['result']
                resp.data.append(data)

            if "pingbo" in x.keys():
                sql = "select * from dj_pinbo_wagers WHERE wagerId='{}' ".format(x['pingbo'])
                listRest = yield from conn._exeCute(sql)
                pinbo_row = yield from listRest.fetchone()
                data = cData()
                data.orders = pinbo_row['wagerId']
                data.accountId = pinbo_row['loginId'][7:]
                messageData=json.loads(pinbo_row['messageData'])
                messageData = json.loads(messageData)
                data.product = '平博体育'
                data.time = strToTimestamp(messageData['wagerDateFm'])
                data.game = messageData['league']
                data.msg = messageData["eventName"]
                #todo 玩法
                data.content = "{}/{}@{}".format(pingboBetType[messageData['betType']],messageData['selection'],pinbo_row['odds'])
                data.money = float("%.2f"%round(pinbo_row['stake'],2))
                data.winning = float("%.2f"%round(pinbo_row['winLoss'],2))
                data.status=pinbo_row['status']
                resp.data.append(data)

        resp.count=count
        resp.ret=errorLogic.success[0]
        if pn==1:
            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "查询注单信息",
                'actionTime': getNow(),
                'actionMethod': methodName,
                'actionDetail': "查询用户：{}，注单信息".format(userId),
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(resp)
    except exceptionLogic as e:
        logging.exception(e)
        raise e
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)
