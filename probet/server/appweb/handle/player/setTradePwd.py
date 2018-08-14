import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from logic.regex import precompile
from lib import certifytoken
from lib.pwdencrypt import PwdEncrypt
from lib.jsonhelp import classJsonDump
from lib.tool import user_token_required


class cData():
    def __init__(self):
        self.tradePwd = 0

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """设置交易密码"""
    objRsp = cResp()

    TradePwd = dict_param.get("tradePwd", "")
    TradePwd2 = dict_param.get("tradePwd2", "")
    strAccountId = dict_param.get("accountId", "")

    if not all([TradePwd, TradePwd2]):
        raise exceptionLogic(errorLogic.client_param_invalid)
    if TradePwd != TradePwd2:
        raise exceptionLogic(errorLogic.player_pwd_pwd2_not_same)
    if precompile.TradePassword.search(TradePwd) is None:
        raise exceptionLogic(errorLogic.player_TradePwd_length_out_of_range)
    objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
    strTradePwd = PwdEncrypt().create_md5(TradePwd)
    objPlayerData.strTradePassword = strTradePwd
    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)

    objRsp.data = cData()
    if objPlayerData.strTradePassword:
        objRsp.data.tradePwd = 1
    else:
        objRsp.data.tradePwd = 0

    return classJsonDump.dumps(objRsp)