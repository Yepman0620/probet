import asyncio
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from config.commissionConfig import commission_config
from lib.jsonhelp import classJsonDump
from lib.timehelp import timeHelp
from datawrapper.agentDataOpWrapper import getDepositDrawingPoundage,getAgentConfig
from lib.tool import agent_token_required


class cData():
    def __init__(self):
        self.proportion = 0.0
        self.allAccount = 0
        self.newAccount = 0
        self.activelyAccount = 0
        self.netProfit = 0

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@agent_token_required
@asyncio.coroutine
def handleHttp(request: dict):
    """代理每月下线用户信息，用于代理后台首页展示"""
    objRep = cResp()

    agentId = request.get('agentId', '')
    pn = request.get('pn', 1)

    if not pn:
        raise exceptionLogic(errorLogic.client_param_invalid)

    start_time = timeHelp.monthStartTimestamp()
    startTime = timeHelp.getNow() - 30*86400
    endTime = timeHelp.getNow()

    agentConfig = yield from getAgentConfig()
    allAccountNum = yield from classSqlBaseMgr.getInstance().getAccountCountByAgent(agentId)
    newAccountNum = yield from classSqlBaseMgr.getInstance().getNewAccountCount(agentId, start_time, endTime)
    activelyAccountNum = yield from classSqlBaseMgr.getInstance().getActivelyAccount(agentId, startTime, endTime)
    pinboAllWinLoss = yield from classSqlBaseMgr.getInstance().getAccountPingboAllWinLoss(agentId, start_time, endTime)
    probetAllWinLoss = yield from classSqlBaseMgr.getInstance().getAccountProbetAllWinCoin(agentId, start_time, endTime)
    probetWinLoss = round(probetAllWinLoss)
    pinboWinLoss = round(pinboAllWinLoss * 100)
    # 平台费
    if pinboWinLoss >= 0:
        pingboPlatformCost = 0
    else:
        pingboPlatformCost = round(-pinboWinLoss * agentConfig['平博体育'])
    if probetWinLoss >= 0:
        probetPlatformCost = 0
    else:
        probetPlatformCost = round(-probetWinLoss * agentConfig['电竞竞猜'])
    pingboBackWater = yield from classSqlBaseMgr.getInstance().getAccountPinboBackWater(agentId, start_time, endTime)
    probetBackWater = yield from classSqlBaseMgr.getInstance().getAccountProbetBackWater(agentId, start_time, endTime)
    activetyBonus = yield from classSqlBaseMgr.getInstance().getAccountActivetyBonus(agentId, start_time, endTime)

    # 反水
    backWater = round(pingboBackWater + probetBackWater)
    # 返奖
    activetyBonus = round(activetyBonus)
    # 存提手续费
    depositDrawingPoundage = yield from getDepositDrawingPoundage(agentId, start_time, endTime)

    # 净利润，净输赢
    netProfit = probetWinLoss + pingboPlatformCost + pinboWinLoss + probetPlatformCost + depositDrawingPoundage + activetyBonus + backWater
    if netProfit <= 0:
        netProfit = -netProfit
        for var_value in commission_config.values():
            if var_value['leastNetWin'] <= netProfit <= var_value['mostNetWin']:
                level = var_value['level']
                proportion = agentConfig[level]
    else:
        proportion = agentConfig['一档']

    objRep.data = cData()
    objRep.data.proportion = '{}%'.format(proportion*100)
    objRep.data.allAccount = allAccountNum
    objRep.data.newAccount = newAccountNum
    objRep.data.activelyAccount = activelyAccountNum
    objRep.data.netProfit = '%.2f'%round(-netProfit/100,2)
    objRep.data.appProportion = proportion
    return classJsonDump.dumps(objRep)

