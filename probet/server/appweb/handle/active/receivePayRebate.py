import asyncio
from lib.jsonhelp import classJsonDump
from appweb.logic.active import joinOncePayRebateActive,checkActiveData
from lib.tool import user_token_required
from error.errorCode import errorLogic,exceptionLogic

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = {}

@user_token_required
@asyncio.coroutine
def handleHttp(dictParam: dict):
    objResp = cResp()
    strAccountId = dictParam.get('accountId','')
    iActiveId = int(dictParam.get('activeId',''))

    if iActiveId <= 0:
        raise exceptionLogic(errorLogic.active_requirements_not_met)

    yield from checkActiveData(strAccountId)

    yield from joinOncePayRebateActive(strAccountId, iActiveId)

    return classJsonDump.dumps(objResp)