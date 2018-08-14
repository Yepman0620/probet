import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from logic.regex import precompile
from lib.pwdencrypt import PwdEncrypt


@asyncio.coroutine
def handleHttp(dict_param: dict):
    """设置新密码"""

    strEmail = dict_param.get("email", "")
    strPhone = dict_param.get("phoneNum", "")
    strNewPwd = dict_param.get("newPwd", "")
    strNewPwd2 = dict_param.get("newPwd2", "")
    if not all([strNewPwd, strNewPwd2]):
        raise exceptionLogic(errorLogic.client_param_invalid)
    # 验证密码的格式是否正确
    if precompile.Password.search(strNewPwd) is None:
        raise exceptionLogic(errorLogic.player_pwd_length_out_of_range)
    if strNewPwd != strNewPwd2:
        raise exceptionLogic(errorLogic.player_pwd_pwd2_not_same)
    if strPhone and strEmail:
        raise exceptionLogic(errorLogic.client_param_invalid)
    if strEmail == "" and strPhone == "":
        raise exceptionLogic(errorLogic.client_param_invalid)
    if strPhone:
        strAccountId = yield from classDataBaseMgr.getInstance().getPhoneAccountMapping(strPhone)
        if not strAccountId:
            raise exceptionLogic(errorLogic.player_data_not_found)

        objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
        if objPlayerData is None:
            raise exceptionLogic(errorLogic.player_data_not_found)
        else:
            strPwd = PwdEncrypt().create_md5(strNewPwd)
            objPlayerData.strPassword = strPwd
            yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)

    if strEmail:
        strAccountId = yield from classDataBaseMgr.getInstance().getEmailAccountMapping(strEmail)

        objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
        if objPlayerData is None:
            raise exceptionLogic(errorLogic.player_data_not_found)
        else:
            strPwd = PwdEncrypt().create_md5(strNewPwd)
            objPlayerData.strPassword = strPwd
            yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)

