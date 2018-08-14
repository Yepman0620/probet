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
    """app佣金报表"""
    objRep = cResp()

    agentId = request.get('agentId', '')
    dateTime = request.get('date', 0)
    if not dateTime:
        raise exceptionLogic(errorLogic.client_param_invalid)

    year = timeHelp.getYear(dateTime)
    month = timeHelp.getMonth(dateTime)
    if month <= 1:
        preYear = year - 1
        preMonth = 12
    else:
        preYear = year
        preMonth = month - 1

    try:
        with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
            sql_pre = "select netProfit,balance from dj_agent_commission where agentId=%s and dateYear=%s and dateMonth=%s"
            params_pre = [agentId, preYear, preMonth]
            ret = yield from conn.execute(sql_pre, params_pre)
            if ret.rowcount <= 0:
                pre_netProfit = 0.00
                pre_balance = 0.00
            else:
                for var in ret:
                    pre_netProfit = var.netProfit
                    pre_balance = var.balance

            sql = "select * from dj_agent_commission where agentId=%s and dateYear=%s and dateMonth=%s"
            params = [agentId, year, month]
            result = yield from conn.execute(sql,params)
            if result.rowcount <= 0:
                return classJsonDump.dumps(objRep)
            else:
                for var_row in result:
                    commissionDict = {}
                    productList = []
                    pingboDict = {}
                    probetDict = {}

                    pingboDict['name'] = '平博体育'
                    pingboDict['winLoss'] = '%.2f' % round(var_row.pingboWinLoss / 100, 2)
                    pingboDict['platformCost'] = '%.2f' % round(var_row.pingboCost / 100, 2)
                    pingboDict['total'] = '%.2f' % round((var_row.pingboWinLoss+var_row.pingboCost) / 100, 2)
                    productList.append(pingboDict)

                    probetDict['name'] = '电竞竞猜'
                    probetDict['winLoss'] = '%.2f' % round(var_row.probetWinLoss / 100, 2)
                    probetDict['platformCost'] = '%.2f' % round(var_row.probetCost / 100, 2)
                    probetDict['total'] = '%.2f' % round((var_row.probetWinLoss+var_row.probetCost) / 100, 2)
                    productList.append(probetDict)

                    commissionDict['product'] = productList
                    commissionDict['subtotal'] = '%.2f' % round((var_row.pingboWinLoss+var_row.pingboCost+var_row.probetWinLoss+var_row.probetCost) / 100, 2)
                    commissionDict['depositDrawingCost'] = '%.2f'%round(var_row.depositDrawingCost/100,2)
                    commissionDict['dividend'] = '%.2f'%round((var_row.backWater+var_row.bonus)/100,2)
                    commissionDict['commissionRate'] = '{}%'.format(var_row.commissionRate*100)
                    commissionDict['pre_netProfit'] = '%.2f'%round(pre_netProfit/100,2)
                    commissionDict['pre_balance'] = '%.2f'%round(-(pre_balance/100),2)
                    commissionDict['balance'] = '%.2f'%round(-(var_row.balance/100),2)
                    commissionDict['commission'] = '%.2f' % round(var_row.commission / 100, 2)

                    objRep.data.append(commissionDict)
            return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)




