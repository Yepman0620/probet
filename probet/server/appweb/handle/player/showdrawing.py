import asyncio

from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib import certifytoken
from lib.tool import user_token_required


class cData():
    def __init__(self):
        self.iCoreCoin = 0
        self.iGuessCoin = 0
        # self.iPinbetCoin = 0
        self.bankCard = []
        self.realname = ""
        self.phone = ""
        self.drawingLimit = 0


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """提款入口"""
    objRsp = cResp()

    strAccountId = dict_param.get("accountId", "")

    objPlayerData  = yield from classDataBaseMgr.getInstance().getPlayerData(strAccountId)
    # 获取可提现额度
    drawinglimit = round((objPlayerData.iCoin - objPlayerData.iNotDrawingCoin) / 100, 2)
    objRsp.data = cData()
    objRsp.data.iCoreCoin = "%.2f" % round(objPlayerData.iCoin/100, 2)
    objRsp.data.iGuessCoin = "%.2f" % round(objPlayerData.iGuessCoin/100, 2)
    objRsp.data.drawingLimit = drawinglimit
    objRsp.data.bankCard = objPlayerData.arrayBankCard
    objRsp.data.phone = objPlayerData.strPhone
    objRsp.data.realname = objPlayerData.strRealName
    if objPlayerData.strTradePassword:
        objRsp.data.tradePwd = 1  # 表示已经设置了交易密码
    else:
        objRsp.data.tradePwd = 0  # 表示没有设置交易密码

    return classJsonDump.dumps(objRsp)














