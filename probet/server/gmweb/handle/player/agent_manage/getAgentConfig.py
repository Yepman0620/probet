import asyncio
import json
import logging

from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow

class cData():
    def __init__(self):
        self.name =''
        self.rate = 0
        self.kind = 0

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('代理管理')
@asyncio.coroutine
def handleHttp(request: dict):
    """代理管理"""
    objRep = cResp()
    agentConfigs=yield from classDataBaseMgr.getInstance().getAgentConfig()

    for bytesAgent in agentConfigs:
        data = cData()
        data.name=bytesAgent.strName
        data.rate=bytesAgent.iRate
        data.kind=bytesAgent.iKind
        objRep.data.append(data)

    fileName = __name__
    nameList = fileName.split('.')
    methodName = nameList.pop()
    # 日志
    dictActionBill = {
        'billType': 'adminActionBill',
        'accountId': request.get('accountId', ''),
        'action': "查询代理各项费率",
        'actionTime': getNow(),
        'actionMethod': methodName,
        'actionDetail': "查询代理各项费率",
        'actionIp': request.get('srcIp', ''),
    }
    logging.getLogger('bill').info(json.dumps(dictActionBill))
    return classJsonDump.dumps(objRep)

