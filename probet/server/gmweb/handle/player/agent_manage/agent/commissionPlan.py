import asyncio
from config.commissionConfig import commission_config
from error.errorCode import exceptionLogic, errorLogic
from lib.jsonhelp import classJsonDump
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from lib.tool import agent_token_required
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.agentDataOpWrapper import getAgentConfig


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@agent_token_required
@asyncio.coroutine
def handleHttp(request: dict):
    """佣金计划"""
    objRep = cResp()

    agentConfig = yield from getAgentConfig()
    for var_value in commission_config.values():
        level = var_value['level']
        proportion = agentConfig[level]
        var_value['proportion'] = '{}%'.format(proportion*100)


    objRep.data.append(commission_config[1])
    objRep.data.append(commission_config[2])
    objRep.data.append(commission_config[3])
    objRep.data.append(commission_config[4])
    objRep.data.append(commission_config[5])
    return classJsonDump.dumps(objRep)

