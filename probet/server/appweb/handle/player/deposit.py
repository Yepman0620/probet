import asyncio
import logging
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib import certifytoken, constants
from lib.jsonhelp import classJsonDump
import random
from logic.logicmgr import checkParamValid as cpv
from appweb.logic.paycore import generalPayOrder
from logic.logicmgr import orderGeneral
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from lib.tool import user_token_required


class enumPayType(object):
    BankTransfer = "BankTransfer"            # 银行卡转账
    AlipayTransfer = "AlipayTransfer"        # 支付宝转账
    AlipayCode = "AlipayCode"                # 支付宝扫码
    UnionpayCode = "UnionpayCode"            # 银联扫码
    QQpayCode = "QQpayCode"                  # QQ支付扫码
    WeixinTransfer = "WeixinTransfer"        # 微信转账


class cData():
    def __init__(self):
        self.iCoin = 0
        self.payeeCardInfo = {}
        self.iSaveCoin = 0


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """存款"""
    objRsp = cResp()

    strAccountId = dict_param.get("accountId", "")
    strToken = dict_param.get("token", "")
    strPayType = dict_param.get("payType", "")
    # iTradeType = dict_param.get("tradeType", 0)
    money = dict_param.get("money", "")
    if not all([strAccountId, strToken, money]):
        raise exceptionLogic(errorLogic.client_param_invalid)
    if cpv.checkIsString(money):
        raise exceptionLogic(errorLogic.client_param_invalid)
    fMoney = float(money)
    if not cpv.checkIsFloat(fMoney):
        raise exceptionLogic(errorLogic.client_param_invalid)
    iCoin = int(fMoney * 100)
    if not cpv.checkIsInt(iCoin):
        raise exceptionLogic(errorLogic.client_param_invalid)

    certifytoken.certify_token(strAccountId, strToken)

    objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(strAccountId)
    if objPlayerData is None:
        raise exceptionLogic(errorLogic.player_data_not_found)
    if strToken != objPlayerData.strToken:
        raise exceptionLogic(errorLogic.login_token_not_valid)

    PayTypeList = []
    for var in constants.DEPOSIT_LIST:
        PayTypeList.append(var["desc"])

    if strPayType not in PayTypeList:
        raise exceptionLogic(errorLogic.pay_type_not_valid)

    if strPayType == enumPayType.BankTransfer:
        # 银行转账
        accountInfoList = yield from classSqlBaseMgr.getInstance().getAllBankInfo()

        objRsp.data = cData()
        objRsp.data.iCoin = "%.2f" % round(objPlayerData.iCoin / 100, 2)
        objRsp.data.iSaveCoin = "%.2f" % round(iCoin / 100, 2)
        try:
            objRsp.data.payeeCardInfo = random.choice(accountInfoList)
        except Exception as e:
            logging.error(repr(e))
            raise exceptionLogic(errorLogic.pay_channel_not_support)
        orderId=orderGeneral.generalOrderId()
        yield from generalPayOrder(orderId,"","",strAccountId,iCoin,dict_param.get("srcIp",""),"银行卡转账",
                               objRsp.data.payeeCardInfo["accountId"])

        # 构造回包
        objRsp.data.payOrder = orderId
        return classJsonDump.dumps(objRsp)

    elif strPayType == enumPayType.AlipayTransfer:
        # 支付宝转账
        accountInfoList = yield from classSqlBaseMgr.getInstance().getAllAlipayInfo()

        objRsp.data = cData()
        objRsp.data.iCoin = "%.2f" % round(objPlayerData.iCoin / 100, 2)
        objRsp.data.iSaveCoin = "%.2f" % round(iCoin / 100, 2)
        try:
            objRsp.data.payeeCardInfo = random.choice(accountInfoList)
        except Exception as e:
            logging.error(repr(e))
            raise exceptionLogic(errorLogic.pay_channel_not_support)
        orderId = orderGeneral.generalOrderId()
        yield from generalPayOrder(orderId, "","", strAccountId, iCoin, dict_param.get("srcIp", ""),
                                   "支付宝转账",objRsp.data.payeeCardInfo["accountId"])
        objRsp.data.payOrder = orderId
        return classJsonDump.dumps(objRsp)

    elif strPayType == enumPayType.WeixinTransfer:
        # 微信转账
        accountInfoList = yield from classSqlBaseMgr.getInstance().getAllWeixinInfo()

        objRsp.data = cData()
        objRsp.data.iCoin = "%.2f" % round(objPlayerData.iCoin / 100, 2)
        objRsp.data.iSaveCoin = "%.2f" % round(iCoin / 100, 2)
        try:
            objRsp.data.payeeCardInfo = random.choice(accountInfoList)
        except Exception as e:
            logging.error(repr(e))
            raise exceptionLogic(errorLogic.pay_channel_not_support)
        orderId = orderGeneral.generalOrderId()
        yield from generalPayOrder(orderId, "","", strAccountId, iCoin, dict_param.get("srcIp", ""),
                                   "微信转账",objRsp.data.payeeCardInfo["accountId"])
        objRsp.data.payOrder = orderId
        return classJsonDump.dumps(objRsp)


