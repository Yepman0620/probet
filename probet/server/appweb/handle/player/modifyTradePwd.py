import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from logic.regex import precompile
from lib import certifytoken
from lib.pwdencrypt import PwdEncrypt
from lib.tool import user_token_required


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """更改交易密码"""

    OldTradePwd = dict_param.get("oldTradePwd", "")
    NewTradepwd = dict_param.get("newTradePwd", "")
    NewTradepwd2 = dict_param.get("newTradePwd2", "")
    strAccountId = dict_param.get("accountId", "")
    if not all([OldTradePwd, NewTradepwd, NewTradepwd2]):
        raise exceptionLogic(errorLogic.client_param_invalid)
    if precompile.TradePassword.search(NewTradepwd) is None:
        raise exceptionLogic(errorLogic.player_TradePwd_length_out_of_range)
    if NewTradepwd != NewTradepwd2:
        raise exceptionLogic(errorLogic.player_pwd_pwd2_not_same)
    strTradePwd = PwdEncrypt().create_md5(NewTradepwd)
    strOldTradePwd = PwdEncrypt().create_md5(OldTradePwd)

    objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)

    if objPlayerData.strTradePassword == strTradePwd:
        raise exceptionLogic(errorLogic.login_pwd_same_old)

    if objPlayerData.strTradePassword != strOldTradePwd:
        raise exceptionLogic(errorLogic.login_only_old_pwd_not_valid)

    if objPlayerData.strTradePassword == strTradePwd:
        raise exceptionLogic(errorLogic.login_pwd_same_old)
    else:
        objPlayerData.strTradePassword = strTradePwd
        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)


