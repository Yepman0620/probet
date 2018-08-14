import asyncio
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.jsonhelp import classJsonDump
from lib import certifytoken
from logic.regex import precompile
from lib.tool import user_token_required


class cData():
    def __init__(self):
        self.email = ""


class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """绑定邮箱"""
    objRsp = cResp()
    strAccountId = dict_param.get("accountId", "")

    objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)

    if objPlayerData.strEmail:
        # 构造回包
        objRsp.data = cData()
        objRsp.data.email = objPlayerData.strEmail

        return classJsonDump.dumps(objRsp)
    else:
        sCode = str(dict_param.get("iCode", ""))
        strEmail = dict_param.get("email", "")
        if not all([sCode, strEmail]):
            raise exceptionLogic(errorLogic.client_param_invalid)
        if precompile.EmailRegex.search(strEmail) is None:
            raise exceptionLogic(errorLogic.player_Email_invalid)

        iCode = yield from classDataBaseMgr.getInstance().getEmailVerify(strEmail)
        if not iCode:
            raise exceptionLogic(errorLogic.verify_code_expired)
        if sCode != iCode:
            raise exceptionLogic(errorLogic.verify_code_not_valid)
        else:
            objPlayerData.strEmail = strEmail
            yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)
            yield from classDataBaseMgr.getInstance().setEmailAccountMapping(strEmail, strAccountId)
            yield from classDataBaseMgr.getInstance().delEmailVerify(strEmail)

        # 构造回包
        objRsp.data = cData()
        objRsp.data.email = objPlayerData.strEmail
        return classJsonDump.dumps(objRsp)
