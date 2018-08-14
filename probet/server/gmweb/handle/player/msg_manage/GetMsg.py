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
        self.data = ""


@token_required
@permission_required('公告管理')
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """
    获取消息
    """
    objRsp = cResp()
    iPageNum = int(dict_param.get("pageNum", 1))
    iType = int(dict_param.get("type", 0))
    if not all([iType, iPageNum]):
        raise exceptionLogic(errorLogic.client_param_invalid)
    if iPageNum <= 0:
        raise exceptionLogic(errorLogic.client_param_invalid)

    MsgDataList, count = yield from classSqlBaseMgr.getInstance().getMsg(iType, iPageNum, 10)

    # 构造回包
    objRsp.data = MsgDataList
    objRsp.count = count
    fileName = __name__
    nameList = fileName.split('.')
    methodName = nameList.pop()
    # 日志
    dictActionBill = {
        'billType': 'adminActionBill',
        'accountId': dict_param.get('accountId', ''),
        'action': "获取新闻/公告",
        'actionTime': getNow(),
        'actionMethod': methodName,
        'actionDetail': "获取新闻/公告",
        'actionIp': dict_param.get('srcIp', ''),
    }
    logging.getLogger('bill').info(json.dumps(dictActionBill))
    yield from asyncio.sleep(1)
    return classJsonDump.dumps(objRsp)






