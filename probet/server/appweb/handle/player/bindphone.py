import asyncio
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.jsonhelp import classJsonDump
from lib import certifytoken
from lib.tool import user_token_required


class cData():
    def __init__(self):
        self.phone = ""


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """绑定手机"""
    objRsp = cResp()

    strAccountId = dict_param.get("accountId", "")
    objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
    if objPlayerData.strPhone:
        # 构造回包
        objRsp.data = cData()
        objRsp.data.phone = objPlayerData.strPhone
        return classJsonDump.dumps(objRsp)
    else:
        sCode = str(dict_param.get("iCode", ""))
        strPhone = dict_param.get("phoneNum", "")
        if not all([sCode, strPhone]):
            raise exceptionLogic(errorLogic.client_param_invalid)
        iCode = yield from classDataBaseMgr.getInstance().getPhoneVerify(strPhone)
        if not iCode:
            raise exceptionLogic(errorLogic.verify_code_expired)
        if iCode != sCode:
            raise exceptionLogic(errorLogic.verify_code_not_valid)
        else:
            yield from classDataBaseMgr.getInstance().delPhoneVerify(strPhone)
            objPlayerData.strPhone = strPhone
            yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)
            yield from classDataBaseMgr.getInstance().setPhoneAccountMapping(strPhone, strAccountId)

        # 构造回包
        objRsp.data = cData()
        objRsp.data.phone = strPhone
        return classJsonDump.dumps(objRsp)
