import asyncio
from lib.jsonhelp import classJsonDump
from logic.logicmgr.checkParamValid import checkIsFloat
from error.errorCode import exceptionLogic,errorLogic
from appweb.handle.pay.logic.payWarp import lpayPayOrder

class cData():
    def __init__(self):
        self.payUrl = ""
        self.urlType = 0
        self.goodsName = ""
        self.goodsPrice = ""
        self.payOrder = ""

class cResp():
    def __init__(self):
        self.ret = ""
        self.retDes = ""
        self.data = ""


@asyncio.coroutine
def handleHttp(dictParam: dict):


    fRmbFen = float(dictParam.get('rmb', "0"))
    if not checkIsFloat(fRmbFen):
        raise exceptionLogic(errorLogic.client_param_invalid)
    # 客户的给的是分
    iRmbFen = int(fRmbFen * 100)

    if iRmbFen < 100 or iRmbFen > 300000:
        raise exceptionLogic(errorLogic.pay_online_amount_limit)

    try:
        #检查用户是否登录,检查用户token
        strAccountId = str(dictParam.get("accountId",""))
        strToken = str(dictParam.get("token",""))
    except:
        raise exceptionLogic(errorLogic.client_param_invalid)

    if len(strAccountId) <= 0:
        raise exceptionLogic(errorLogic.player_id_empty)

    objResp = cResp()
    #objResp.data = yield from pocoPayOrder(strAccountId,iRmbFen,"alipay","wap",dictParam.get("srcIp", ""),pocoWrapPayOrderCall)
    objResp.data = yield from lpayPayOrder(strAccountId,iRmbFen,"alipay_wap",dictParam.get("strIp",""))

    return classJsonDump.dumps(objResp)

