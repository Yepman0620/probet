import asyncio
from lib.jsonhelp import classJsonDump

class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = ""


@asyncio.coroutine
def handleHttp(dict_param: dict):
    objRsp = cResp()

    return classJsonDump.dumps(objRsp)

