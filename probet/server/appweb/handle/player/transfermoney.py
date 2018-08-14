import asyncio

from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib import certifytoken
from appweb.logic import pinboDeposit
from logic.logicmgr import checkParamValid as cpv
from datawrapper.playerDataOpWrapper import addPlayerBill
from logic.enum.enumCoinOp import CoinOp
import logging
from lib.tool import user_token_required


class cData():
    def __init__(self):
        self.iCoin = 0
        self.iGuessCoin = 0
        self.orderdata = {}


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """转账"""
    objRsp = cResp()

    strAccountId = dict_param.get("accountId", "")
    TurnOut = dict_param.get("Turnout", "")
    TurnIn = dict_param.get("Turnin", "")
    money = dict_param.get("money", "")

    if not all([TurnOut, TurnIn, money]):
        raise exceptionLogic(errorLogic.client_param_invalid)

    if cpv.checkIsString(money):
        raise exceptionLogic(errorLogic.client_param_invalid)

    fMoney = float(money)
    if not cpv.checkIsFloat(fMoney):
        raise exceptionLogic(errorLogic.client_param_invalid)
    fMoney = float("%.2f"%fMoney)

    iCoin = int(fMoney*100)
    if not cpv.checkIsInt(iCoin):
        raise exceptionLogic(errorLogic.client_param_invalid)

    if TurnOut != "中心钱包" and TurnIn != "中心钱包":
        raise exceptionLogic(errorLogic.client_param_invalid)

    objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
    tradeData = None
    if TurnOut == "中心钱包" and TurnIn == "平博钱包":
        if iCoin > int(objPlayerData.iCoin):
            raise exceptionLogic(errorLogic.player_coin_not_enough)
        objPlayerData.iCoin -= iCoin
        iBalance = objPlayerData.iCoin - iCoin

        # 触发另一个平台的转账功能
        status = yield from pinboDeposit.deposit(kind='deposit', accountId=strAccountId, amount=fMoney)
        if status == 1:
            objPlayerData.iPingboCoin += iCoin
        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)

        tradeData = yield from addPlayerBill(strAccountId,iCoin,iBalance,CoinOp.coinOpTrans,status,TurnOut,TurnIn)

    elif TurnOut == "中心钱包" and TurnIn == "电竞钱包":
        if iCoin > int(objPlayerData.iCoin):
            raise exceptionLogic(errorLogic.player_coin_not_enough)
        objPlayerData.iCoin -= iCoin
        objPlayerData.iGuessCoin += iCoin
        iBalance = objPlayerData.iCoin - iCoin
        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)

        tradeData = yield from addPlayerBill(strAccountId, iCoin,iBalance, CoinOp.coinOpTrans, 1,TurnOut,TurnIn)

    elif TurnIn == "中心钱包" and TurnOut == "平博钱包":
        # 触发另一个平台的转账功能
        status = yield from pinboDeposit.deposit(kind='withdraw', accountId=strAccountId, amount=fMoney)
        if status == 1:
            objPlayerData.iCoin += iCoin
            objPlayerData.iPingboCoin -= iCoin
            iBalance = objPlayerData.iCoin + iCoin
            yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)

        tradeData = yield from addPlayerBill(strAccountId, iCoin,iBalance, CoinOp.coinOpTrans, status,TurnOut, TurnIn)


    elif TurnIn == "中心钱包" and TurnOut == "电竞钱包":
        if iCoin > int(objPlayerData.iGuessCoin):
            raise exceptionLogic(errorLogic.player_coin_not_enough)

        objPlayerData.iCoin += iCoin
        objPlayerData.iGuessCoin -= iCoin
        iBalance = objPlayerData.iCoin + iCoin
        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)
        tradeData = yield from addPlayerBill(strAccountId, iCoin, iBalance,CoinOp.coinOpTrans, 1,TurnOut,TurnIn)
    else:
        logging.error("unkown trun way {} {}".format(TurnIn,TurnOut))


    objRsp.data = cData()
    objRsp.data.iCoin = "%.2f"%round(objPlayerData.iCoin/100, 2)
    objRsp.data.iGuessCoin = "%.2f"%round(objPlayerData.iGuessCoin/100, 2)
    tradeData.iCoin =float("%.2f"%round(tradeData.iCoin/100,2))
    objRsp.data.orderdata = tradeData

    return classJsonDump.dumps(objRsp)
