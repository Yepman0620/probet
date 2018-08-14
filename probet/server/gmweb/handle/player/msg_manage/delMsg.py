import asyncio
import json
import logging
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from lib.timehelp.timeHelp import getNow


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('新闻管理')
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """
    删除消息
    """
    objRsp = cResp()

    strMsgId = dict_param.get("msgId", "")
    iType = dict_param.get("type", 0)
    if not all([strMsgId, iType]):
        raise exceptionLogic(errorLogic.client_param_invalid)

    yield from classSqlBaseMgr.getInstance().delMsg(strMsgId)
    yield from classDataBaseMgr.getInstance().delMsg(iType,strMsgId)
    MsgDataList, count = yield from classSqlBaseMgr.getInstance().getMsg(iType, 1, 10)
    # count = yield from classDataBaseMgr.getInstance().getMsgCount(iType)

    # 构造回包
    objRsp.data = MsgDataList
    objRsp.count = count
    yield from asyncio.sleep(1)
    fileName = __name__
    nameList = fileName.split('.')
    methodName = nameList.pop()
    # 日志
    dictActionBill = {
        'billType': 'adminActionBill',
        'accountId': dict_param.get('accountId', ''),
        'action': "删除消息/新闻/公告消息",
        'actionTime': getNow(),
        'actionMethod': methodName,
        'actionDetail': "删除消息/新闻/公告消息Id：{}".format(strMsgId),
        'actionIp': dict_param.get('srcIp', ''),
    }
    logging.getLogger('bill').info(json.dumps(dictActionBill))
    return classJsonDump.dumps(objRsp)




