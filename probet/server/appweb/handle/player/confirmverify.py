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
    """校验验证码"""
    objRsp = cResp()
    try:
        strPhone = dict_param["phoneNum"]
        strEmail = dict_param["email"]
    except Exception as e:
        raise exceptionLogic(errorLogic.client_param_invalid)

    if all([strPhone, strEmail]):
        raise exceptionLogic(errorLogic.client_param_invalid)

    if strPhone:
        sCode = dict_param.get("iCode", "")
        if not sCode:
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
        sCode = dict_param.get("iCode", "")
        if not sCode:
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


