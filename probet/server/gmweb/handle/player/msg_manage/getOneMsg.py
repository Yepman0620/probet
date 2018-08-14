import asyncio
import json
import logging
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from lib.timehelp.timeHelp import getNow


class cData():
    def __init__(self):
        self.Msg = ""

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@token_required
@permission_required('新闻管理')
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """
    获取指定消息
    """
    objRsp = cResp()

    strMsgId = dict_param.get("msgId", "")
    iType = dict_param.get("type", 0)
    if not strMsgId:
        raise exceptionLogic(errorLogic.client_param_invalid)

    MsgData = yield from classDataBaseMgr.getInstance().getOneMsg(iType, strMsgId)

    if MsgData is None:
        return classJsonDump.dumps(objRsp)
    # 构造回包
    objRsp.data = cData()
    objRsp.data.Msg = MsgData
    fileName = __name__
    nameList = fileName.split('.')
    methodName = nameList.pop()
    # 日志
    dictActionBill = {
        'billType': 'adminActionBill',
        'accountId': dict_param.get('accountId', ''),
        'action': "获取消息",
        'actionTime': getNow(),
        'actionMethod': methodName,
        'actionDetail': "获取消息Id：{}".format(strMsgId),
        'actionIp': dict_param.get('srcIp', ''),
    }
    logging.getLogger('bill').info(json.dumps(dictActionBill))
    return classJsonDump.dumps(objRsp)




