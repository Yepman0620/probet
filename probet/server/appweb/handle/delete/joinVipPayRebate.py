import asyncio
from lib.jsonhelp import classJsonDump
from appweb.logic.active import joinVipPayRebateActive
from lib import certifytoken



class cResp():
    def __init__(self):
        self.ret = ""
        self.retDes = ""
        self.data = []


@asyncio.coroutine
def handleHttp(dictParam: dict):
    objResp = cResp()
    strAccountId = dictParam.get('accountId','')
    iLevel = int(dictParam.get('level',0))
    strToken = dictParam.get('token','')

    certifytoken.certify_token(strAccountId, strToken)

    yield from joinVipPayRebateActive(strAccountId, iLevel)

    return classJsonDump.dumps(objResp)

