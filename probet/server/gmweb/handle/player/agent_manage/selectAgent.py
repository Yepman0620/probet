import asyncio
import json
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from datawrapper.agentDataOpWrapper import getDepositDrawingPoundage,getAgentConfig
from config.commissionConfig import commission_config
from lib.timehelp import timeHelp

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []
        self.count = 0


@token_required
@permission_required('代理概况')
@asyncio.coroutine
def handleHttp(request: dict):
    """代理概况查询"""
    objRep = cResp()
    agentId = request.get('agentId', '')
    startTime = request.get('startTime', 0)
    endTime = request.get('endTime', 0)
    pn = request.get('pn', 1)

    if not all([startTime, endTime, pn]):
        raise exceptionLogic(errorLogic.client_param_invalid)
    year = timeHelp.getYear(startTime)
    month = timeHelp.getMonth(startTime)
    if month <= 1:
        preYear = year - 1
        preMonth = 12
    else:
        preYear = year
        preMonth = month - 1

    try:
        agentConfig = yield from getAgentConfig()
        if not agentConfig:
            raise exceptionLogic(errorLogic.data_not_valid)

        agentList, count = yield from classSqlBaseMgr.getInstance().getAgentData(agentId,pn)
        for agentId in agentList:
            with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
                sql = "select balance from dj_agent_commission where agentId=%s and dateYear=%s and dateMonth=%s"
                result = yield from conn.execute(sql, [agentId, preYear, preMonth])
                if result.rowcount <= 0:
                    preBalance = 0
                else:
                    for var_row in result:
                        preBalance = var_row.balance
            allAccountNum = yield from classSqlBaseMgr.getInstance().getAccountCountByAgent(agentId)
            activelyAccountNum = yield from classSqlBaseMgr.getInstance().getActivelyAccount(agentId, startTime, endTime)
            depositNum = yield from classSqlBaseMgr.getInstance().getAccountAllDeposit(agentId, startTime, endTime)
            drawingNum = yield from classSqlBaseMgr.getInstance().getAccountAllDrawing(agentId, startTime, endTime)
            balanceNum = yield from classSqlBaseMgr.getInstance().getAccountAllCoin(agentId, startTime, endTime)

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
            platformCost = pingboPlatformCost + probetPlatformCost
            #反水红利
            pingboBackWater = yield from classSqlBaseMgr.getInstance().getAccountPinboBackWater(agentId, startTime, endTime)
            probetBackWater = yield from classSqlBaseMgr.getInstance().getAccountProbetBackWater(agentId, startTime, endTime)
            activetyBonus = yield from classSqlBaseMgr.getInstance().getAccountActivetyBonus(agentId, startTime, endTime)

            # 反水
            backWater = round(pingboBackWater + probetBackWater)
            # 返奖
            activetyBonus = round(activetyBonus)
            # 存提手续费
            depositDrawingPoundage = yield from getDepositDrawingPoundage(agentId, startTime, endTime)

            # 净利润，净输赢
            netWin = probetWinLoss + pingboPlatformCost + pinboWinLoss + probetPlatformCost + depositDrawingPoundage + activetyBonus + backWater
            if netWin <= 0:
                a = -netWin
            else:
                a = netWin
            for var_value in commission_config.values():
                if var_value['leastNetWin'] <= a <= var_value['mostNetWin']:
                    level = var_value['level']
                    proportion = agentConfig[level]
            iBalance = netWin + preBalance
            if iBalance < 0:
                # 佣金
                commission = round(-iBalance * proportion)
            else:
                commission = 0

            agentSurvey = {}
            agentSurvey['agentId'] = agentId
            agentSurvey['allAccountNum'] = allAccountNum
            agentSurvey['activelyAccountNum'] = activelyAccountNum
            agentSurvey['depositNum'] = '%.2f'%round(depositNum/100, 2)
            agentSurvey['drawingNum'] = '%.2f'%round(drawingNum/100, 2)
            agentSurvey['balanceNum'] = '%.2f'%round(balanceNum/100, 2)
            agentSurvey['netWin'] = '%.2f'%round(netWin/100,2)
            agentSurvey['platformCost'] = '%.2f' % round(platformCost / 100, 2)
            agentSurvey['depositdrawingCost'] = '%.2f'%round(depositDrawingPoundage/100,2)
            agentSurvey['commission'] = '%.2f'%round(commission/100,2)
            agentSurvey['commissionRate'] = proportion
            agentSurvey['dividend'] = '%.2f'%((backWater+activetyBonus)/100)
            agentSurvey['preBalance'] = '%.2f'%(preBalance/100)
            objRep.data.append(agentSurvey)
        if pn==1:
            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "代理概况查询",
                'actionTime': timeHelp.getNow(),
                'actionMethod': methodName,
                'actionDetail': "代理：{}概况查询".format(agentId),
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))
        objRep.count = count
        return classJsonDump.dumps(objRep)

    except Exception as e:
        logging.error(repr(e))




