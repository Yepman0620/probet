import asyncio
import json
import logging
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.timehelp import timeHelp


class cData():
    def __init__(self):
        self.phone = ""


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('代理账号管理')
@asyncio.coroutine
def handleHttp(request: dict):
    """代理账号管理"""
    agentId = request.get('agentId', '')
    lockTime = request.get('lockTime', '')
    lockReason = request.get('lockReason', '')
    status = request.get('status', '')

    if not agentId:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        objAgentData = yield from classDataBaseMgr.getInstance().getAgentData(agentId)
        if objAgentData is None:
            logging.debug(errorLogic.agent_data_not_found)
            raise exceptionLogic(errorLogic.agent_data_not_found)

        if status == 0:
            # 解封
            objAgentData.iStatus = status
            objAgentData.iLockStartTime = 0
            objAgentData.iLockEndTime = 0
            objAgentData.strLockReason = ""
        else:
            # 冻结账号
            if not all([lockTime, lockReason]):
                logging.debug(errorLogic.lockTime_or_lockReason_lack)
                raise exceptionLogic(errorLogic.lockTime_or_lockReason_lack)
            objAgentData.iStatus = 1
            objAgentData.iLockStartTime=timeHelp.getNow()
            objAgentData.iLockEndTime = timeHelp.getNow() + int(lockTime)
            objAgentData.strLockReason = lockReason

        yield from classDataBaseMgr.getInstance().setAgentData(objAgentData)

        resp = cResp()
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "代理账号管理修改",
            'actionTime': timeHelp.getNow(),
            'actionMethod': methodName,
            'actionDetail': "代理账号管理修改：{}".format(agentId),
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(resp)
    except exceptionLogic as e:
        logging.error(repr(e))
        raise e

