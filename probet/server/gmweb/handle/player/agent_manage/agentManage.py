import asyncio
import json
import logging
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from logic.data.userData import classConfig
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.timehelp import timeHelp
from logic.logicmgr.checkParamValid import checkIsInt


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('代理管理')
@asyncio.coroutine
def handleHttp(request: dict):
    """新增、删除,修改平台，存取款费率"""
    name=request.get('name','')
    kind=request.get('kind')
    rate = request.get('rate', 0)
    action=request.get('action','')
    if not all([name,action]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    if action not in ['del','add']:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        if action=='del':
            #删除
            if not name:
                logging.debug(errorLogic.client_param_invalid)
                raise exceptionLogic(errorLogic.client_param_invalid)
            ret=yield from classDataBaseMgr.getInstance().delAgentConfig(name)
            if ret<=0:
                logging.debug(errorLogic.data_not_valid)
                raise exceptionLogic(errorLogic.data_not_valid)
        else:
            #新增或修改
            if not all([name,rate,kind]):
                logging.debug(errorLogic.client_param_invalid)
                raise exceptionLogic(errorLogic.client_param_invalid)
            if not checkIsInt(rate):
                logging.debug(errorLogic.client_param_invalid)
                raise exceptionLogic(errorLogic.client_param_invalid)
            agentConfigClass=classConfig()
            agentConfigClass.strName=name
            agentConfigClass.iRate=rate
            agentConfigClass.iKind=kind
            yield from classDataBaseMgr.getInstance().addAgentConfig(agentConfigClass)

        resp = cResp()
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "新增/修改：{} 费率：{}".format(name,rate) if action=='add' else "删除：{} 费率".format(name),
            'actionTime': timeHelp.getNow(),
            'actionMethod': methodName,
            'actionDetail': "新增/修改：{} 费率 :{}".format(name,rate) if action=='add' else "删除：{} 费率".format(name),
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(resp)
    except exceptionLogic as e:
        logging.error(repr(e))
        raise e

