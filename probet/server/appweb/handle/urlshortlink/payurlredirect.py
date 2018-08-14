import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.jsonhelp import classJsonDump
from error.errorCode import errorLogic,exceptionLogic

class cResp():
    def __init__(self):
        self.ret = ""
        self.retDes = ""


@asyncio.coroutine
def handleHttp(dictParam: dict):
    objResp = cResp()

    strShortUrl = dictParam.get("shorturl","")
    if len(strShortUrl) > 0:

        strLongUrl = yield from classDataBaseMgr.getInstance().getPayShortUrl(strShortUrl)
        if strLongUrl is not None:
            objResponse = dictParam.get("resp", None)
            objResponse.headers["Location"] = strLongUrl
            objResponse._status = 302
        else:
            raise exceptionLogic(errorLogic.pay_qrcode_invalid)
            #return "<p>充值失败请稍后再试，如果您有疑问，请联系客服</p><br><p>原因:充值二维码已经实效,请重新下单</p>".encode()


    return classJsonDump.dumps(objResp)
