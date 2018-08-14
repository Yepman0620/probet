import asyncio
import logging
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic,errorLogic
from lib.jsonhelp import classJsonDump


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@asyncio.coroutine
def handleHttp(dict_param: dict):
    """登出"""
    objRep = cResp()

    agentId = dict_param.get('agentId', '')
    if not agentId:
        raise exceptionLogic(errorLogic.client_param_invalid)

    objAgentData = yield from classDataBaseMgr.getInstance().getAgentData(agentId)
    if objAgentData is None:
        raise exceptionLogic(errorLogic.player_data_not_found)
    else:
        objAgentData.strToken = ""
        yield from classDataBaseMgr.getInstance().setAgentData(objAgentData)

    return classJsonDump.dumps(objRep)

