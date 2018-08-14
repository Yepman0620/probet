import asyncio
from gmweb.protocol.gmProtocol import gameTypeMap
from gmweb.utils.tools import token_required
from lib.jsonhelp import classJsonDump

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = {}

@token_required
@asyncio.coroutine
def handleHttp(request: dict):
    """获取所有游戏名"""
    objRep = cResp()
    gameTypeMap['pingbo']='平博'
    objRep.data=gameTypeMap
    return classJsonDump.dumps(objRep)