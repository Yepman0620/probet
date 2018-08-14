import asyncio
import json
import logging
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.timehelp.timeHelp import getNow

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('用户提款管理')
@asyncio.coroutine
def handleHttp(request: dict):
    # 确认提款，审核完成
    accountId=request.get('accountId','')
    orderId=request.get('orderId','')
    reason=request.get('reason','')
    bankOrderId=request.get('bankOrderId','')
    action=request.get('action','')

    if not all([orderId,action]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    if action not in ['confirm','cancel']:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        objCoinHisData = yield from classDataBaseMgr.getInstance().getCoinHisByLock(orderId)
        objPlayerData,objLock=yield from classDataBaseMgr.getInstance().getPlayerDataByLock(objCoinHisData.strAccountId)
        if (objCoinHisData is None) or (objPlayerData is None):
            raise exceptionLogic(errorLogic.player_data_not_found)

        if objCoinHisData.iTradeState != 2:
            raise exceptionLogic(errorLogic.hisCoin_state_not_correct)
        resp = cResp()

        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionIp': request.get('srcIp', ''),
        }

        if action=='confirm':
            if not bankOrderId:
                raise exceptionLogic(errorLogic.client_param_invalid)
            # 日志
            dictWithdrawal = {
                'billType': 'withdrawalBill',
                'orderId': orderId,
                'agentId': objPlayerData.strAgentId,
                'accountId': objPlayerData.strAccountId,
                'withdrawalTime': getNow(),
                'withdrawalCoin': objCoinHisData.iCoin,
                'withdrawalIp': request.get('srcIp',''),
                'cardNum': objCoinHisData.strTransTo,
                'orderState': 1,
                'userType':objPlayerData.iUserType,
                'bankOrderId':bankOrderId
            }
            logging.getLogger('bill').info(json.dumps(dictWithdrawal))

            objCoinHisData.strReviewer=accountId
            objCoinHisData.iTradeState=1
            objCoinHisData.iEndTime=getNow()
            objCoinHisData.strBankOrderId=bankOrderId
            dictActionBill['action'] = "用户提款审核"
            dictActionBill['actionDetail'] = "审核用户提款单号:{}，完成。给用户:{},加钱:{}".format(orderId, objPlayerData.strAccountId,
                                                                                  objCoinHisData.iCoin / 100),

        else:
            #取消提款
            if not reason:
                raise exceptionLogic(errorLogic.client_param_invalid)
            objCoinHisData.strReviewer = accountId
            objPlayerData.iCoin+=objCoinHisData.iCoin
            objCoinHisData.iTradeState = 3
            objCoinHisData.iEndTime = getNow()
            objCoinHisData.strReason = reason
            dictActionBill['action'] = "取消用户提款"
            dictActionBill['actionDetail'] = "取消用户：{} 提款，单号:{}，原因:{}".format(objPlayerData.strAccountId, orderId,
                                                                             reason)

        logging.getLogger('bill').info(json.dumps(dictActionBill))
        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)
        yield from classDataBaseMgr.getInstance().setPlayerCoinRecord(objCoinHisData.strAccountId, objCoinHisData)
        yield from asyncio.sleep(1)
        return classJsonDump.dumps(resp)
    except Exception as e:
        logging.exception(e)
        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData,objLock)
        raise e
