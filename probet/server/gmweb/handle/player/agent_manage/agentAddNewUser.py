import asyncio
import json
import logging

from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from datawrapper.agentDataOpWrapper import getAccountDepositDrawingPoundage,getAgentConfig
from lib.timehelp.timeHelp import getNow


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('代理注册')
@asyncio.coroutine
def handleHttp(request: dict):
    """代理新增线下用户"""
    objRep = cResp()

    agentId = request.get('agentId', '')
    offlineUser=request.get('offlineUser','')

    if not all([agentId, offlineUser]):
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        agentData=yield from classDataBaseMgr.getInstance().getAgentData(agentId)
        if agentData is None:
            # 判断是否是代理
            logging.debug(errorLogic.agent_data_not_found)
            raise exceptionLogic(errorLogic.agent_data_not_found)

        userIsAgent=yield from classDataBaseMgr.getInstance().getAgentData(offlineUser)
        if userIsAgent is not None:
            # 判断新增用户是否是代理
            logging.debug(errorLogic.user_is_agent)
            raise exceptionLogic(errorLogic.user_is_agent)
        # 判断新增用户是否是有代理
        userData,objPlayerLock=yield from classDataBaseMgr.getInstance().getPlayerDataByLock(offlineUser)
        if userData is None:
            logging.debug(errorLogic.player_data_not_found)
            raise exceptionLogic(errorLogic.player_data_not_found)
        if userData.strAgentId!='':
            logging.debug(errorLogic.user_has_agent)
            raise exceptionLogic(errorLogic.user_has_agent)
        userData.strAgentId=agentId
        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(userData,objPlayerLock)

        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "代理新增下线用户",
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionDetail': "给代理：{} 新增下线用户：{}".format(agentId,offlineUser),
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(objRep)

    except Exception as e:
        logging.exception(e)
        raise e