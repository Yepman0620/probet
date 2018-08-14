import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic,errorLogic
from logic.data.userData import classUserData

class cData():
    def __init__(self):
        self.phoneNum = ""
        self.email = ""


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""

@asyncio.coroutine
def handleHttp(dict_param: dict):
    """找回密码时校验验证码"""
    objRsp = cResp()

    strPhone = dict_param.get("phoneNum", "")
    strEmail = dict_param.get("email", "")
    if strPhone and strEmail:
        raise exceptionLogic(errorLogic.player_Email_is_none)
    if strPhone == "" and strEmail == "":
        raise exceptionLogic(errorLogic.client_param_invalid)
    if strPhone:

        try:
            sCode = str(dict_param["iCode"])
        except Exception as e:
            raise exceptionLogic(errorLogic.client_param_invalid)

        iCode = yield from classDataBaseMgr.getInstance().getPhoneVerify(strPhone)

        if not iCode:
            raise exceptionLogic(errorLogic.verify_code_expired)
        if iCode != sCode:
            raise exceptionLogic(errorLogic.verify_code_not_valid)
        yield from classDataBaseMgr.getInstance().delPhoneVerify(strPhone)

        # 构造回包
        objRsp.data = cData()
        objRsp.data = strPhone

        return classJsonDump.dumps(objRsp)

    if strEmail:
        try:
            sCode = str(dict_param["iCode"])
        except Exception as e:
            raise exceptionLogic(errorLogic.client_param_invalid)

        iCode = yield from classDataBaseMgr.getInstance().getEmailVerify(strEmail)

        if not iCode:
            raise exceptionLogic(errorLogic.verify_code_expired)
        if iCode != sCode:
            raise exceptionLogic(errorLogic.verify_code_not_valid)

        yield from classDataBaseMgr.getInstance().delEmailVerify(strEmail)

        # 构造回包
        objRsp.data = cData()
        objRsp.data = strEmail

        return classJsonDump.dumps(objRsp)


