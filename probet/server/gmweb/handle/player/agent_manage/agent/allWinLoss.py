import asyncio
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from lib.timehelp import timeHelp
from datawrapper.agentDataOpWrapper import getDepositDrawingPoundage,getAgentConfig
from config.commissionConfig import commission_config
from lib.tool import agent_token_required


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []
        self.water = 0
        self.winLoss = 0
        self.backWater = 0


@agent_token_required
@asyncio.coroutine
def handleHttp(request: dict):
    """财务报表-总输赢"""
    objRep = cResp()

    agentId = request.get('agentId', '')
    startTime = request.get('startTime', 0)
    endTime = request.get('endTime', 0)

    if not all([startTime, endTime]):
        startTime = timeHelp.monthStartTimestamp()
        endTime = timeHelp.getNow()
    agentConfig = yield from getAgentConfig()
    #输赢
    pinboAllWinLoss = yield from classSqlBaseMgr.getInstance().getAccountPingboAllWinLoss(agentId, startTime, endTime)
    probetAllWinLoss = yield from classSqlBaseMgr.getInstance().getAccountProbetAllWinCoin(agentId, startTime, endTime)
    #流水
    pinboAllWater = yield from classSqlBaseMgr.getInstance().getAccountPingboWater(agentId, startTime, endTime)
    probetAllWater = yield from classSqlBaseMgr.getInstance().getAccountProbetWater(agentId, startTime, endTime)
    #反水红利
    pingboBackWater = yield from classSqlBaseMgr.getInstance().getAccountPinboBackWater(agentId, startTime, endTime)
    probetBackWater = yield from classSqlBaseMgr.getInstance().getAccountProbetBackWater(agentId, startTime, endTime)
    activetyBonus = yield from classSqlBaseMgr.getInstance().getAccountActivetyBonus(agentId, startTime, endTime)

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
    pinboSurvey = {}
    probetSurvey = {}
    # 反水
    backWater = round(pingboBackWater + probetBackWater)
    # 返奖
    activetyBonus = round(activetyBonus)
    # 存提手续费
    depositDrawingPoundage = yield from getDepositDrawingPoundage(agentId, startTime, endTime)
    # 净利润，净输赢
    netProfit = probetWinLoss - pingboPlatformCost + pinboWinLoss - probetPlatformCost + depositDrawingPoundage + backWater + activetyBonus
    if netProfit <= 0:
        netProfit = -netProfit
        for var_value in commission_config.values():
            if var_value['leastNetWin'] <= netProfit <= var_value['mostNetWin']:
                level = var_value['level']
                proportion = agentConfig[level]
    else:
        proportion = agentConfig['一档']

    # 平台净输赢
    pingboNetWinLoss = pinboWinLoss + pingboPlatformCost + round(pingboBackWater)
    probetNetWinLoss = probetWinLoss + probetPlatformCost + round(probetBackWater+activetyBonus)
    if pingboNetWinLoss >= 0:
        pingboCommission = 0
    else:
        pingboCommission = -pingboNetWinLoss * proportion
    if probetNetWinLoss >= 0:
        probetCommission = 0
    else:
        probetCommission = -probetNetWinLoss * proportion

    pinboSurvey['project'] = '平博体育'
    pinboSurvey['winLoss'] = '%.2f'%(-pinboAllWinLoss)
    pinboSurvey['rate'] = '{}%'.format(agentConfig['平博体育']*100)
    pinboSurvey['platformCost'] = '%.2f' % round(pingboPlatformCost / 100, 2)
    pinboSurvey['waterCoin'] = '%.2f'%pinboAllWater
    pinboSurvey['backWater'] = '%.2f'%round(pingboBackWater/100,2)
    pinboSurvey['commission'] = '%.2f'%round(pingboCommission/100,2)

    probetSurvey['project'] = '电竞竞猜'
    probetSurvey['winLoss'] = '%.2f' % round(-probetAllWinLoss / 100, 2)
    probetSurvey['rate'] = '{}%'.format(agentConfig['电竞竞猜']*100)
    probetSurvey['platformCost'] = '%.2f' % round(probetPlatformCost/ 100, 2)
    probetSurvey['waterCoin'] = '%.2f'%round(probetAllWater/100,2)
    probetSurvey['backWater'] = '%.2f'%round(probetBackWater/100,2)
    probetSurvey['commission'] = '%.2f'%round(probetCommission/100,2)

    objRep.data.append(pinboSurvey)
    objRep.data.append(probetSurvey)
    objRep.water = '%.2f'%round((int(pinboAllWater*100) + probetAllWater)/100,2)
    objRep.allWinLoss = '%.2f'%(-(pinboWinLoss+probetWinLoss)/100)
    objRep.allBackWater = '%.2f'%round((pingboBackWater+probetBackWater)/100,2)
    return classJsonDump.dumps(objRep)
