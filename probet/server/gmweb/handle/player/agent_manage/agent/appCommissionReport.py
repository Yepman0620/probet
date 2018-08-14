import asyncio
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from lib.timehelp import timeHelp
from lib.tool import agent_token_required


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@agent_token_required
@asyncio.coroutine
def handleHttp(request: dict):
    """app佣金报表查询"""
    objRep = cResp()

    agentId = request.get('agentId', '')
    dateTime = request.get('date', 0)

    if not dateTime:
        now = timeHelp.getNow()
        year = timeHelp.getYear(now)
        month = timeHelp.getMonth(now)
    else:
        year = timeHelp.getYear(dateTime)
        month = timeHelp.getMonth(dateTime)

    try:
        with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
            sql = "select * from dj_agent_commission where agentId=%s and dateYear=%s and dateMonth=%s"
            params = [agentId, year, month]
            result = yield from conn.execute(sql,params)
            if result.rowcount <= 0:
                return classJsonDump.dumps(objRep)
            else:
                for var_row in result:
                    commissionDict = {}
                    commissionDict['date'] = str(var_row.dateYear)+'/'+str(var_row.dateMonth)
                    commissionDict['activelyAccountNum'] = var_row.activeAccount
                    commissionDict['winLoss'] = '%.2f'%round(var_row.winLoss/100,2)
                    commissionDict['platformCost'] = '%.2f'%round(var_row.platformCost/100,2)
                    commissionDict['depositDrawingCost'] = '%.2f'%round(var_row.depositDrawingCost/100,2)
                    commissionDict['dividend'] = '%.2f'%round((var_row.backWater+var_row.bonus)/100,2)
                    commissionDict['netProfit'] = '%.2f'%round(var_row.netProfit/100,2)
                    commissionDict['commissionRate'] = '{}%'.format(var_row.commissionRate*100)
                    commissionDict['commission'] = '%.2f'%round(var_row.commission/100,2)
                    commissionDict['status'] = var_row.status
                    objRep.data.append(commissionDict)
            return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)




