import asyncio
import json
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.tool import agent_token_required
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from gmweb.protocol.gmProtocol import pingboBetType

class cData():
    def __init__(self):
        self.betId=''

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@agent_token_required
@asyncio.coroutine
def handleHttp(request: dict):
    """获取用户平博注单信息"""
    objRep = cResp()

    accountId = request.get('accountId', '')
    kind=request.get('kind','')
    pn = request.get('pn', 1)
    startTime = request.get('startTime', 0)
    endTime = request.get('endTime', 0)

    if not all([pn,kind,accountId,startTime,endTime]):
        raise exceptionLogic(errorLogic.client_param_invalid)
    if kind not in ['pingbo','probet']:
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
            if kind=='pingbo':
                id="probet."+accountId
                sql="select * from dj_pinbo_wagers WHERE loginId =%s and wagerDateFm between %s and %s ORDER by wagerDateFm desc limit %s offset %s"
                sql_count="select count(wagerId) from dj_pinbo_wagers WHERE loginId=%s and wagerDateFm between %s and %s"
                sql_params=[id,startTime,endTime,MSG_PAGE_COUNT,(pn-1)*MSG_PAGE_COUNT]
                sql_count_params=[id,startTime,endTime]
            else:
                sql="select * from dj_bet WHERE accountId=%s and dj_bet.time between %s and %s ORDER BY dj_bet.time desc limit %s offset %s"
                sql_count = "select count(guessUId) from dj_bet WHERE accountId=%s and dj_bet.time between %s and %s"
                sql_params = [accountId,startTime,endTime,MSG_PAGE_COUNT,(pn-1)*MSG_PAGE_COUNT]
                sql_count_params = [accountId,startTime,endTime]
            retCount=yield from conn.execute(sql_count,sql_count_params)
            count=yield from retCount.fetchone()
            objRep.count =count[0]
            result=yield from conn.execute(sql,sql_params)
            resList=yield from result.fetchall()
            for x in resList:
                data=cData()
                if kind=='pingbo':
                    data.betId=x['wagerId']
                    data.accountId=x['loginId'][7:]
                    data.betTime=x['wagerDateFm']
                    messageData = json.loads(x['messageData'])
                    messageData = json.loads(messageData)
                    if x['settleDateFm']==0:
                        data.betInfo = "/"
                        data.betCoin = "未结算"
                        data.winLoss = "未结算"
                    else:
                        data.betInfo="{} @{} {}".format(pingboBetType[messageData['betType']],x['odds'],messageData['selection'])
                        data.betCoin="%.2f"%(x['toRisk'])
                        data.winLoss="%.2f"%(x['winLoss'])
                        if x['status'] == 'PENDING':
                            data.state = 0
                        elif x['status'] == 'OPEN':
                            data.state = 4
                        elif x['status'] == 'CANCELLED':
                            data.state = 3
                        elif x['status'] == 'DELETED':
                            data.state = 5
                        elif x['status'] == 'SETTLED' and x['winLoss'] > 0:
                            data.state = 1
                        elif x['status'] == 'SETTLED' and x['winLoss'] < 0:
                            data.state = 2
                else:
                    data.betId=x['guessUId']
                    data.accountId=x['accountId']
                    data.betTime=x['time']
                    ctr = json.loads(x['ctr'])
                    if x['resultTime']==0:
                        data.betInfo="/"
                        data.betCoin="未结算"
                        data.winLoss="未结算"
                    else:
                        data.betInfo="{} @ {} {}".format(x['guessName'],ctr[x.chooseId]['fRate'],ctr[x.chooseId]['strChooseName'])
                        data.betCoin="%.2f"%round(x['betCoin']/100,2)
                        data.winLoss="%.2f"%round((x['winCoin']-x['betCoin'])/100,2)
                        if x.result < 4:
                            data.state = 0
                        elif (x.result == 5 or x.result == 6 or x.result == 7 or x.result == 8) and x.winCoin-x.betCoin <= 0:
                            data.state = 3
                        elif x.winCoin-x.betCoin > 0:
                            data.state = 1
                        elif x.winCoin-x.betCoin <= 0:
                            data.state = 2
                objRep.data.append(data)
        return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)
