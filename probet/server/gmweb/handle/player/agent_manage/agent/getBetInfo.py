import asyncio
import json
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from gmweb.protocol.gmProtocol import pingboBetType
from lib.tool import agent_token_required
from lib.timehelp import timeHelp
from datetime import datetime
import ast
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
    """获取平博注单信息"""
    objRep = cResp()

    agentId = request.get('agentId', '')
    kind=request.get('kind','')
    pn = request.get('pn', 1)
    date = request.get('date', '')

    if not all([pn,kind,date]):
        raise exceptionLogic(errorLogic.client_param_invalid)
    if kind not in ['pingbo','probet']:
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
            year = int(date[0:4])
            month = int(date[5:])
            begin = datetime(year, month, 1)
            if month == 12:
                end = datetime(year+1, 1, 1)
            else:
                end = datetime(year,month+1,1)
            start_time = timeHelp.date2timestamp(begin)
            end_time = timeHelp.date2timestamp(end)
            sql="select accountId from dj_account WHERE agentId= %s "
            result=yield from conn.execute(sql,[agentId])
            accountIds=yield from result.fetchall()
            if len(accountIds)==0:
                objRep.count=0
                return classJsonDump.dumps(objRep)
            else:
                ids=[x[0] for x in accountIds]

            if kind=='pingbo':
                ids=["probet."+x for x in ids]
                sql="select * from dj_pinbo_wagers WHERE loginId IN (%s) and wagerDateFm between {} and {} ORDER by wagerDateFm desc"%",".join(["%s"]*len(ids))
                sql_count="select count(wagerId) from dj_pinbo_wagers WHERE loginId IN (%s) and wagerDateFm between {} and {}"%",".join(["%s"]*len(ids))
            else:
                sql="select * from dj_bet WHERE accountId in (%s) and dj_bet.time between {} and {} ORDER BY dj_bet.time desc"%",".join(["%s"]*len(ids))
                sql_count = "select count(guessUId) from dj_bet WHERE accountId IN (%s) and dj_bet.time between {} and {}"%",".join(["%s"]*len(ids))
            sql=sql+" limit %s offset %s"
            sql=sql.format(start_time,end_time)
            sql_count=sql_count.format(start_time,end_time)
            retCount=yield from conn.execute(sql_count,ids)
            count=yield from retCount.fetchone()
            objRep.count =count[0]
            ids.extend([MSG_PAGE_COUNT,(pn-1)*MSG_PAGE_COUNT])
            result=yield from conn.execute(sql,ids)
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
                            data.state = 2
                        elif x['status'] == 'SETTLED' and x['winLoss'] < 0:
                            data.state = 1


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
                        data.betInfo="{} @{} {}".format(x['guessName'],ctr[x.chooseId]['fRate'],ctr[x.chooseId]['strChooseName'])
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
