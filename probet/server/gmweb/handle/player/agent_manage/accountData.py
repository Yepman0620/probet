import asyncio
import json
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from datawrapper.agentDataOpWrapper import getAccountDepositDrawingPoundage,getAgentConfig
from lib.timehelp.timeHelp import getNow


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
    """下线用户详情"""
    objRep = cResp()

    agentId = request.get('agentId', '')
    startTime = request.get('startTime', 0)
    endTime = request.get('endTime', 0)
    pn = request.get('pn', 1)

    if not all([startTime, endTime, pn]):
        raise exceptionLogic(errorLogic.client_param_invalid)
    agentConfig = yield from getAgentConfig()
    try:
        accountList, count = yield from classSqlBaseMgr.getInstance().getAccountDataByAgent(agentId, startTime, endTime, pn)
        if len(accountList) <= 0:
            return classJsonDump.dumps(objRep)
        else:
            accountDataList = []
            for accountData in accountList:
                accountDataDict = {}
                accountId = accountData['accountId']
                regTime = accountData['regTime']
                loginTime = accountData['loginTime']
                balance = yield from classSqlBaseMgr.getInstance().getAccountAllBalance(accountId)
                deposit = yield from classSqlBaseMgr.getInstance().getAccountDeposit(accountId, startTime, endTime)
                drawing = yield from classSqlBaseMgr.getInstance().getAccountDrawing(accountId, startTime, endTime)

                pinboAllWinLoss = yield from classSqlBaseMgr.getInstance().getAccountPingboWinLoss(accountId, startTime,endTime)
                probetAllWinLoss = yield from classSqlBaseMgr.getInstance().getAccountProbetWinCoin(accountId, startTime,endTime)
                probetWinLoss = round(probetAllWinLoss)
                pinboWinLoss = round(pinboAllWinLoss * 100)
                #返利
                allDividend = yield from classSqlBaseMgr.getInstance().getAccountDividend(accountId, startTime,endTime)
                dividend = round(allDividend)
                #存提手续费
                depositDrawingPoundage = yield from getAccountDepositDrawingPoundage(accountId, startTime, endTime)
                #平台费
                if pinboWinLoss>=0:
                    pingboPlatformCost = 0
                else:
                    pingboPlatformCost = round(-pinboWinLoss * agentConfig['平博体育'])
                if probetWinLoss >= 0:
                    probetPlatformCost = 0
                else:
                    probetPlatformCost = round(-probetWinLoss * agentConfig['电竞竞猜'])
                if deposit > 0:
                    isDeposit = '是'
                else:
                    isDeposit = '否'

                accountDataDict['accountId'] = accountId
                accountDataDict['regTime'] = regTime
                accountDataDict['loginTime'] = loginTime
                accountDataDict['balance'] = "%.2f"%round(balance/100, 2)
                accountDataDict['deposit'] = "%.2f"%round(deposit/100, 2)
                accountDataDict['drawing'] = "%.2f"%round(drawing/100, 2)
                accountDataDict['netWin'] = "%.2f"%round((pinboWinLoss+probetWinLoss+dividend+depositDrawingPoundage+pingboPlatformCost+probetPlatformCost)/100, 2)
                accountDataDict['depositUser'] = isDeposit
                accountDataList.append(accountDataDict)
            objRep.data = accountDataList
            objRep.count = count
            if pn==1:
                fileName = __name__
                nameList = fileName.split('.')
                methodName = nameList.pop()
                # 日志
                dictActionBill = {
                    'billType': 'adminActionBill',
                    'accountId': request.get('accountId', ''),
                    'action': "查询代理下线详情",
                    'actionTime': getNow(),
                    'actionMethod': methodName,
                    'actionDetail': "查询代理：{} 下线详情".format(agentId),
                    'actionIp': request.get('srcIp', ''),
                }
                logging.getLogger('bill').info(json.dumps(dictActionBill))
            return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)