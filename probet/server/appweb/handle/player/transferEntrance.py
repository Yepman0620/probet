import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib import certifytoken, constants
from lib.tool import user_token_required


class cData():
    def __init__(self):
        self.iCoreCoin = 0
        self.iGuessCoin = 0
        # self.iPinbetCoin = 0
        self.Turnout = []
        self.Turnin = []


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """转账入口"""
    objRsp = cResp()

    strAccountId = dict_param.get("accountId", "")
    objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(strAccountId)

    objRsp.data = cData()
    objRsp.data.iCoreCoin = "%.2f"%round(objPlayerData.iCoin/100, 2)
    objRsp.data.iGuessCoin = "%.2f"%round(objPlayerData.iGuessCoin/100, 2)
    # objRsp.data.iPinbetCoin = 1000
    objRsp.data.Turnout.extend(constants.WALLET_LIST)
    objRsp.data.Turnin.extend(constants.WALLET_LIST)

    return classJsonDump.dumps(objRsp)


























