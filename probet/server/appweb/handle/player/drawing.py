import asyncio
from lib.pwdencrypt import PwdEncrypt
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib import certifytoken
from logic.logicmgr import checkParamValid as cpv
from logic.enum.enumCoinOp import CoinOp
from datawrapper.playerDataOpWrapper import addPlayerBill
from lib.tool import user_token_required


class cData():
    def __init__(self):
        self.iCoin = 0
        self.newDrawingLimit = 0


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """提款"""
    objRsp = cResp()

    strAccountId = dict_param.get("accountId", "")
    strCardNum = str(dict_param.get("cardNum", ""))
    TradePwd = dict_param.get("tradePwd", "")
    money = dict_param.get("money", "")
    if not all([strCardNum, money]):
        raise exceptionLogic(errorLogic.client_param_invalid)
    if cpv.checkIsString(money):
        raise exceptionLogic(errorLogic.client_param_invalid)
    fMoney = float(money)
    if not cpv.checkIsFloat(fMoney):
        raise exceptionLogic(errorLogic.client_param_invalid)
    iCoin = int(fMoney * 100)
    if not cpv.checkIsInt(iCoin):
        raise exceptionLogic(errorLogic.client_param_invalid)

    strTradePwd = PwdEncrypt().create_md5(TradePwd)

    objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
    if not objPlayerData.strTradePassword:
        raise exceptionLogic(errorLogic.trade_pwde_not_bind)
    if strTradePwd != objPlayerData.strTradePassword:
        raise exceptionLogic(errorLogic.trade_pwde_not_valid)

    # 获取可提现额度
    drawinglimit = round((objPlayerData.iCoin - objPlayerData.iNotDrawingCoin) / 100, 2)

    Coin = round(iCoin/100)
    if not cpv.checkIsInt(Coin):
        raise exceptionLogic(errorLogic.player_drawing_coin_not_int)
    if Coin > drawinglimit:
        raise exceptionLogic(errorLogic.player_drawing_not_enough)
    if objPlayerData.iCoin < iCoin:
        raise exceptionLogic(errorLogic.player_coin_not_enough)
    else:
        balance = objPlayerData.iCoin - iCoin
        # redis 事务操作以及余额的处理
        objPlayerData.iCoin -= iCoin
        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)

        yield from addPlayerBill(strAccountId,iCoin,balance,CoinOp.coinOpDraw,2,"中心钱包", strCardNum)

    newdrawinglimit = drawinglimit - Coin
    objRsp.data = cData()
    objRsp.data.iCoin = "%.2f"%round(objPlayerData.iCoin/100, 2)
    objRsp.data.newDrawingLimit = newdrawinglimit

    return classJsonDump.dumps(objRsp)
























