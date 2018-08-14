import asyncio
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from lib.timehelp import timeHelp
from lib.tool import agent_token_required
from datawrapper.agentDataOpWrapper import getDepositDrawingPoundage,getAgentConfig


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@agent_token_required
@asyncio.coroutine
def handleHttp(request: dict):
    """财务报表-平台费"""
    objRep = cResp()

    agentId = request.get('agentId', '')
    startTime = int(request.get('startTime', 0))
    endTime = int(request.get('endTime', 0))

    if not all([startTime, endTime]):
        startTime = timeHelp.monthStartTimestamp()
        endTime = timeHelp.getNow()
    agentConfig = yield from getAgentConfig()
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

    pinboSurvey = {}
    probetSurvey = {}

    pinboSurvey['project'] = '平博体育'
    pinboSurvey['winLoss'] = '%.2f'%(-pinboAllWinLoss)
    pinboSurvey['rate'] = '{}%'.format(agentConfig['平博体育']*100)
    pinboSurvey['platformCost'] = '%.2f' % round(pingboPlatformCost/ 100,2)

    probetSurvey['project'] = '电竞竞猜'
    probetSurvey['winLoss'] = '%.2f'%round(-probetAllWinLoss/100,2)
    probetSurvey['rate'] = '{}%'.format(agentConfig['电竞竞猜']*100)
    probetSurvey['platformCost'] = '%.2f' % round(probetPlatformCost/100,2)

    objRep.data.append(pinboSurvey)
    objRep.data.append(probetSurvey)
    return classJsonDump.dumps(objRep)
