import asyncio
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.tool import agent_token_required
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from lib.timehelp import timeHelp
from datawrapper.agentDataOpWrapper import getDepositDrawingPoundage,getAgentConfig


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@agent_token_required
@asyncio.coroutine
def handleHttp(request: dict):
    """财务报表"""
    objRep = cResp()

    agentId = request.get('agentId', '')
    startTime = request.get('startTime', 0)
    endTime = request.get('endTime', 0)

    if not all([startTime, endTime]):
        startTime = timeHelp.monthStartTimestamp()
        endTime = timeHelp.getNow()
    try:
        agentConfig = yield from getAgentConfig()
        if not agentConfig:
            raise exceptionLogic(errorLogic.data_not_valid)
        # allAccountNum = yield from classSqlBaseMgr.getInstance().getAccountCountByAgent(agentId)
        # activelyAccountNum = yield from classSqlBaseMgr.getInstance().getActivelyAccount(agentId, startTime, endTime)
        depositNum = yield from classSqlBaseMgr.getInstance().getAccountAllDeposit(agentId, startTime, endTime)
        drawingNum = yield from classSqlBaseMgr.getInstance().getAccountAllDrawing(agentId, startTime, endTime)
        # balanceNum = yield from classSqlBaseMgr.getInstance().getAccountAllCoin(agentId, startTime, endTime)
        pingboBackWater = yield from classSqlBaseMgr.getInstance().getAccountPinboBackWater(agentId, startTime, endTime)
        probetBackWater = yield from classSqlBaseMgr.getInstance().getAccountProbetBackWater(agentId, startTime, endTime)
        activetyBonus = yield from classSqlBaseMgr.getInstance().getAccountActivetyBonus(agentId, startTime, endTime)
        pinboAllWinLoss = yield from classSqlBaseMgr.getInstance().getAccountPingboAllWinLoss(agentId, startTime, endTime)
        probetAllWinLoss = yield from classSqlBaseMgr.getInstance().getAccountProbetAllWinCoin(agentId, startTime, endTime)
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
        platformCost = probetPlatformCost + pingboPlatformCost

        agentSurvey = {}
        allWinLoss = probetWinLoss+pinboWinLoss
        dividend = round(pingboBackWater + probetBackWater + activetyBonus)
        depositDrawingPoundage = yield from getDepositDrawingPoundage(agentId, startTime, endTime)
        netWin = allWinLoss + platformCost + dividend + depositDrawingPoundage

        # agentSurvey['allAccountNum'] = allAccountNum
        # agentSurvey['activelyAccountNum'] = activelyAccountNum
        agentSurvey['depositNum'] = '%.2f' % round(depositNum / 100, 2)
        agentSurvey['drawingNum'] = '%.2f' % round(drawingNum / 100, 2)
        agentSurvey['allWinLoss'] = '%.2f' % round(-allWinLoss/100, 2)
        agentSurvey['netWin'] = '%.2f' % round(-netWin / 100, 2)
        agentSurvey['platformCost'] = '%.2f' % round(platformCost / 100, 2)
        agentSurvey['dividend'] = '%.2f' % (dividend / 100)
        agentSurvey['poundage'] = '%.2f' % (depositDrawingPoundage / 100)

        objRep.data.append(agentSurvey)
        return classJsonDump.dumps(objRep)

    except Exception as e:
        logging.exception(e)
