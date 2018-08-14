import asyncio
import json
import logging
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.timehelp.timeHelp import getNow
from lib.observer import classSubject
from event.eventDefine import event_exchange_coin


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('线下充值管理')
@asyncio.coroutine
def handleHttp(request: dict):
    # 确认、取消、删除线下充值到账
    account=request.get('account','')
    payOrder=request.get('payOrder','')
    action=request.get('action','')
    reason=request.get('reason','')

    if not all([payOrder,action]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    if action not in ['cancel','confirm']:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        objCoinHisData = yield from classDataBaseMgr.getInstance().getCoinHisByLock(payOrder)
        objPayData=yield from classDataBaseMgr.getInstance().getPayOrder(payOrder)
        objPlayerData,objLock1=yield from classDataBaseMgr.getInstance().getPlayerDataByLock(objCoinHisData.strAccountId)
        if (objCoinHisData is None) or (objPlayerData is None) or (objPayData is None):
            raise exceptionLogic(errorLogic.player_data_not_found)
        if objCoinHisData.iTradeState not in [2,3]:
            raise exceptionLogic(errorLogic.hisCoin_state_not_correct)
        objCoinHisData.strReviewer = account['accountId']
        objCoinHisData.iEndTime = getNow()
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

            dictActionBill['action']="确认线下充值到账"
            dictActionBill['actionDetail']= "确认线下充值到账，给用户:{}，充值:{}，单号:{}".format(objPlayerData.strAccountId, objCoinHisData.iCoin / 100,payOrder),
            # 日志
            dictPay = {
                'billType': 'payBill',
                'orderId': payOrder,
                'agentId': objPlayerData.strAgentId,
                'accountId': objPlayerData.strAccountId,
                'payTime': getNow(),
                'payCoin': objCoinHisData.iCoin,
                'payIp': objPlayerData.strLastLoginIp,
                'payChannel': objPayData.strPayChannel,
                'orderState': 1,
                'firstPayCoin': objPlayerData.iFirstPayCoin,
                'thirdPayOrder': "",
                'thirdPayName': "",
                'firstPayTime': objPlayerData.iFirstPayTime,
            }
            # 判断是否是每月首冲vip活动

            logging.getLogger('bill').info(json.dumps(dictPay))
            if objPlayerData.iFirstPayCoin==0:
                objPlayerData.iFirstPayCoin=objCoinHisData.iCoin
                objPlayerData.iFirstPayTime=getNow()

            objCoinHisData.iTradeState=1
            objPlayerData.iCoin+=objCoinHisData.iCoin
            objPlayerData.iNotDrawingCoin += objCoinHisData.iCoin
            #TODO open the logic
            yield from classSubject.getInstance().notify(event_exchange_coin, playerData=objPlayerData,
                                                         payCoin=objPayData.iBuyCoin, orderTime=objPayData.iOrderTime)

        else:
            if not reason:
                logging.debug(errorLogic.not_cancel_reason)
                raise exceptionLogic(errorLogic.not_cancel_reason)

            dictActionBill['action'] = "取消线下充值到账"
            dictActionBill['actionDetail'] = "取消线下充值到账用户:{}，取消单号:{}，原因:{}".format(objPlayerData.strAccountId,payOrder,reason),
            objCoinHisData.iTradeState=3
            objCoinHisData.strReason=reason
        yield from classDataBaseMgr.getInstance().setPlayerCoinRecord(objCoinHisData.strAccountId,objCoinHisData)

        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock1)
        resp=cResp()
        resp.ret=errorLogic.success[0]

        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(resp)

    except exceptionLogic as e:
        logging.error(repr(e))
        raise e
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)
