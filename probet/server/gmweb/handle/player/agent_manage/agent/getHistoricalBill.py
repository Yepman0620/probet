import asyncio
import json
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.tool import agent_token_required
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from lib.timehelp import timeHelp


class cData():
    def __init__(self):
        self.yearMonth=''   #年月
        self.regCount=0     #注册用户
        self.loginCount=0   #活跃用户
        self.totalWater=0   #总流水
        self.winLoss=0      #净输赢
        self.commission=0   #佣金

class cResp():
    def __init__(self):
        self.count=0
        self.ret = 0
        self.retDes = ""
        self.data = []


@agent_token_required
@asyncio.coroutine
def handleHttp(request: dict):
    """获取每月历史账单信息"""
    objRep = cResp()

    agentId = request.get('agentId', '')
    pn = request.get('pn', 1)

    if not pn:
        raise exceptionLogic(errorLogic.client_param_invalid)
    year = timeHelp.getYear(timeHelp.getNow())
    month = timeHelp.getMonth(timeHelp.getNow())

    try:
        with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
            sql="select * from dj_agent_commission WHERE agentId=%s ORDER BY dateYear DESC ,dateMonth DESC limit %s offset %s"
            listRet=yield from conn.execute(sql,[agentId,MSG_PAGE_COUNT,(pn-1)*MSG_PAGE_COUNT])
            resList=yield from listRet.fetchall()
            for x in resList:
                if x['dateYear'] == year and x['dateMonth'] == month:
                    continue
                data=cData()
                data.yearMonth="{}/{}".format(x['dateYear'],x['dateMonth'])
                data.regCount=x['newAccount']
                data.loginCount=x['activeAccount']
                data.totalWater="%.2f"%round(x['water']/100,2)
                data.winLoss="%.2f"%round(x['netProfit']/100,2)
                data.commission="%.2f"%round(x['commission']/100,2)
                objRep.data.append(data)
            count_sql = "select count(billId) from dj_agent_commission WHERE agentId=%s"
            countRet=yield from conn.execute(count_sql,[agentId])
            count=yield from countRet.fetchone()
            objRep.count=count[0]
        return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)
