import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from logic.regex import precompile
from lib import certifytoken
from lib.pwdencrypt import PwdEncrypt
from lib.jsonhelp import classJsonDump
from lib.tool import user_token_required


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """更改密码"""
    objRsp = cResp()

    strOldPwd = dict_param.get("oldPwd", "")
    Newpwd = dict_param.get("newPwd", "")
    Newpwd2 = dict_param.get("newPwd2", "")
    strAccountId = dict_param.get("accountId", "")
    if not all([strOldPwd, Newpwd, Newpwd2]):
        raise exceptionLogic(errorLogic.client_param_invalid)
    if precompile.Password.search(Newpwd) is None:
        raise exceptionLogic(errorLogic.player_pwd_length_out_of_range)
    objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
    strPwd = PwdEncrypt().create_md5(strOldPwd)
    strNewpwd = PwdEncrypt().create_md5(Newpwd)

    if strPwd != objPlayerData.strPassword:
        raise exceptionLogic(errorLogic.login_only_old_pwd_not_valid)

    if objPlayerData.strPassword == strNewpwd:
        raise exceptionLogic(errorLogic.login_pwd_same_old)
    if Newpwd != Newpwd2:
        raise exceptionLogic(errorLogic.player_pwd_pwd2_not_same)
    else:
        objPlayerData.strPassword = strNewpwd
        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)

    return classJsonDump.dumps(objRsp)
