import asyncio
import json
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow
from datawrapper.agentDataOpWrapper import getAccountDepositDrawingPoundage,getAgentConfig


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('代理概况')
@asyncio.coroutine
def handleHttp(request: dict):
    """佣金详情查询"""
    objRep = cResp()

    agentId = request.get('agentId', '')
    startTime = request.get('startTime', 0)
    endTime = request.get('endTime', 0)
    if not all([startTime, endTime, agentId]):
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        agentConfig = yield from getAgentConfig()
        if not agentConfig:
            raise exceptionLogic(errorLogic.data_not_valid)

        pinboAllWinLoss = yield from classSqlBaseMgr.getInstance().getAccountPingboAllWinLoss(agentId, startTime,
                                                                                           endTime)
        probetAllWinLoss = yield from classSqlBaseMgr.getInstance().getAccountProbetAllWinCoin(agentId, startTime,
                                                                                            endTime)
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
        pingboBackWater = yield from classSqlBaseMgr.getInstance().getAccountPinboBackWater(agentId, startTime,endTime)
        probetBackWater = yield from classSqlBaseMgr.getInstance().getAccountProbetBackWater(agentId, startTime,endTime)
        activetyBonus = yield from classSqlBaseMgr.getInstance().getAccountActivetyBonus(agentId, startTime, endTime)

        pinboSurvey = {}
        probetSurvey = {}

        pingboNetProfit = pinboWinLoss+pingboPlatformCost+round(pingboBackWater)
        pinboSurvey['project'] = '平博体育'
        pinboSurvey['winLoss'] = '%.2f'%pinboAllWinLoss
        pinboSurvey['platformCost'] = '%.2f'%round(pingboPlatformCost/100,2)
        pinboSurvey['netProfit'] = '%.2f'%round(pingboNetProfit/100,2)
        pinboSurvey['dividend'] = '%.2f'%round(pingboBackWater/100,2)

        probetNetProfit = probetWinLoss+probetPlatformCost+round(probetBackWater+activetyBonus)
        probetSurvey['project'] = '电竞竞猜'
        probetSurvey['winLoss'] = '%.2f'%round(probetAllWinLoss/100,2)
        probetSurvey['platformCost'] = '%.2f'%round(probetPlatformCost/100,2)
        probetSurvey['netProfit'] = '%.2f'%round(probetNetProfit/100,2)
        probetSurvey['dividend'] = '%.2f'%round((probetBackWater+activetyBonus)/100,2)

        objRep.data.append(pinboSurvey)
        objRep.data.append(probetSurvey)
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "查询代理佣金详情",
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionDetail': "查询代理：{} 佣金详情".format(agentId),
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.error(repr(e))
        raise e




