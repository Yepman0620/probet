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
        self.count = 0


@agent_token_required
@asyncio.coroutine
def handleHttp(request: dict):
    """佣金报表"""
    objRep = cResp()

    agentId = request.get('agentId', '')
    startTime = request.get('startTime', 0)
    endTime = request.get('endTime', 0)
    pn = request.get('pn', 1)
    if not pn:
        raise exceptionLogic(errorLogic.client_param_invalid)

    if not all([startTime, endTime]):
        sql = "select * from dj_agent_commission where agentId=%s order by dateYear desc,dateMonth desc limit %s offset %s"
        params=[agentId,10,(pn-1)*10]
    else:
        startYear = timeHelp.getYear(startTime)
        startMonth = timeHelp.getMonth(startTime)
        endYear = timeHelp.getYear(endTime)
        endMonth = timeHelp.getMonth(endTime)
        sql = "select * from dj_agent_commission where agentId=%s and (dateYear between %s and %s) and (dateMonth between %s and %s) order by dateYear desc,dateMonth desc limit %s offset %s"
        params=[agentId,startYear,endYear,startMonth,endMonth,10,(pn-1)*10]
    try:
        with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
            result = yield from conn.execute(sql,params)
            if result.rowcount <= 0:
                return classJsonDump.dumps(objRep)
            else:
                for var_row in result:
                    # productList = []
                    # pingboDict = {}
                    # probetDict = {}
                    # pingboDict['name'] = '平博体育'
                    # pingboDict['winLoss'] = '%.2f'%round(var_row.pingboWinLoss/100,2)
                    # pingboDict['platformCost'] = '%.2f'%round(var_row.pingboCost/100,2)
                    # pingboDict['rate'] = '{}%'.format(agentConfig['平博体育']*100)
                    # productList.append(pingboDict)
                    #
                    # probetDict['name'] = '电竞竞猜'
                    # probetDict['winLoss'] = '%.2f'%round(var_row.probetWinLoss/100,2)
                    # probetDict['platformCost'] = '%.2f'%round(var_row.probetCost/100,2)
                    # probetDict['rate'] = '{}%'.format(agentConfig['电竞竞猜'] * 100)
                    # productList.append(probetDict)

                    commissionDict = {}
                    commissionDict['date'] = str(var_row.dateYear)+'/'+str(var_row.dateMonth)
                    commissionDict['activelyAccountNum'] = var_row.activeAccount
                    commissionDict['pingboWinLoss'] = '%.2f'%round(var_row.pingboWinLoss/100,2)
                    commissionDict['probetWinLoss'] = '%.2f'%round(var_row.probetWinLoss/100,2)
                    commissionDict['pingboCost'] = '%.2f'%round(var_row.pingboCost/100,2)
                    commissionDict['probetCost'] = '%.2f'%round(var_row.probetCost/100,2)
                    commissionDict['pingboRate'] = '{}%'.format(var_row.probetRate * 100)
                    commissionDict['probetRate'] = '{}%'.format(var_row.pingboRate * 100)
                    commissionDict['depositDrawingCost'] = '%.2f'%round(var_row.depositDrawingCost/100,2)
                    commissionDict['backWater'] = '%.2f'%round(var_row.backWater/100,2)
                    commissionDict['bonus'] = '%.2f'%round(var_row.bonus/100,2)
                    commissionDict['netProfit'] = '%.2f'%round(var_row.netProfit/100,2)
                    commissionDict['balance'] = '%.2f'%round(-(var_row.preBalance/100),2)
                    commissionDict['commissionRate'] = '{}%'.format(var_row.commissionRate*100)
                    commissionDict['commission'] = '%.2f'%round(var_row.commission/100,2)
                    commissionDict['status'] = var_row.status
                    objRep.data.append(commissionDict)
        count = yield from classSqlBaseMgr.getInstance().getAgentCommissionCount(agentId,startTime,endTime)
        objRep.count = count
        return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)




