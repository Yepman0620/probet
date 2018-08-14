import asyncio
from error.errorCode import exceptionLogic,errorLogic
from appweb.handle.pay.logic.payWarp import lpayPayOrder
from appweb.proc import procVariable
from logic.logicmgr.checkParamValid import checkIsFloat
from lib.certifytoken import certify_token
from lib.jsonhelp import classJsonDump


class cResp():
    def __init__(self):
        self.ret = ""
        self.retDes = ""
        self.data = ""


@asyncio.coroutine
def handleHttp(dictParam: dict):
    objResp = cResp()

    fRmbFen = float(dictParam.get('rmb', "0"))
    if not checkIsFloat(fRmbFen):
        raise exceptionLogic(errorLogic.client_param_invalid)
    # 客户的给的是分
    iRmbFen = int(fRmbFen * 100)
    # 检查用户是否登录,检查用户token

    strAccountId = str(dictParam["accountId"])
    strToken = str(dictParam.get("token", ""))

    if not procVariable.debug:
        certify_token(strAccountId, strToken)
    #这里用web的
    objResp.data = yield from lpayPayOrder(strAccountId, iRmbFen, "unionpay_wap", dictParam.get("srcIp", ""))

    return classJsonDump.dumps(objResp)