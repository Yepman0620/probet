import asyncio
import json
import logging

from lib.timehelp import timeHelp
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.observer import classSubject
from event.eventDefine import event_pay_success

@asyncio.coroutine
def processPayResult(payOrderId,getRmb):


    objPayOrder, objPayLock = yield from classDataBaseMgr.getInstance().getPayOrderByLock(payOrderId)
    if objPayOrder is None:
        logging.error("payOrderId [{}] is not found".format(payOrderId))
    else:
        if objPayOrder.iBuyCoin != getRmb:
            logging.error("buyCoin is not equal [{}] [{}]".format(objPayOrder.iBuyCoin, getRmb))
            yield from classDataBaseMgr.getInstance().releasePayDataLock(objPayOrder, objPayLock)
        else:
            if False and objPayOrder.iPayTime != 0:
                logging.error("payOrderId payTime not null maybe have finish [{}]".format(payOrderId))
                yield from classDataBaseMgr.getInstance().releasePayDataLock(objPayOrder, objPayLock)
            else:
                objPayOrder.iPayTime = timeHelp.getNow()
                yield from classDataBaseMgr.getInstance().setPayOrderByLock(objPayOrder, objPayLock)
                # 给用户加钱，修改账单数据
                objPlayerData, objPlayerLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(objPayOrder.strAccountId)

                if objPlayerData is None:
                    logging.error("accountId [{}]".format(objPayOrder.strAccountId))
                else:
                    objPlayerData.iCoin += objPayOrder.iBuyCoin
                    if objPlayerData.iFirstPayCoin == 0:
                        # 判断是否是首冲
                        objPlayerData.iFirstPayTime = timeHelp.getNow()
                        objPlayerData.iFirstPayCoin = getRmb

                    # 修改用户的coinHis 状态
                    objCoinHis = yield from classDataBaseMgr.getInstance().getCoinHisByLock(payOrderId)
                    objCoinHis.iTradeState = 1
                    objCoinHis.iEndTime = timeHelp.getNow()
                    yield from classDataBaseMgr.getInstance().setPlayerCoinRecord(objPayOrder.strAccountId,objCoinHis)

                    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData,objPlayerLock)

                    try:
                        # emit the event
                        yield from classSubject.getInstance().notify(event_pay_success,playerData=objPlayerData,payCoin=objPayOrder.iBuyCoin,orderTime=objPayOrder.iOrderTime)

                        # 日志
                        dictPay = {
                            'billType': 'payBill',
                            'orderId': payOrderId,
                            'agentId': objPlayerData.strAgentId,
                            'accountId': objPlayerData.strAccountId,
                            'payTime': timeHelp.getNow(),
                            'payCoin': getRmb,
                            'payIp': objPlayerData.strLastLoginIp,
                            'payChannel': objPayOrder.strPayChannel,
                            'orderState': objCoinHis.iTradeState,
                            'firstPayCoin': objPlayerData.iFirstPayCoin,
                            'thirdPayOrder':objPayOrder.strThirdPayOrder,
                            'thirdPayName': objPayOrder.strThirdPayName,
                            'firstPayTime':objPlayerData.iFirstPayTime,
                        }

                        logging.getLogger('bill').info(json.dumps(dictPay))

                    except Exception as e:
                        logging.exception(e)

                    return 0

    return -1