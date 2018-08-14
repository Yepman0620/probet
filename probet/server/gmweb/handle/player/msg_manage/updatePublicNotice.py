import asyncio
import json
import logging
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from logic.data.userData import classMessageData
from lib.timehelp import timeHelp
import uuid
from gmweb.utils.tools import token_required, permission_required


class getMsgType(object):
    """发布的消息类型"""
    getNoticeType = 1  # 公告
    getNewsType = 2  # 新闻


class cData():
    def __init__(self, iMsgId, strMsgTitle, strMsgDetail, iMsgTime, iMsgType):
        self.msgId = iMsgId
        self.title = strMsgTitle
        self.detail = strMsgDetail
        self.MsgType = iMsgType
        self.msgTime = iMsgTime
        # self.unReadNum = 0


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


def addMsgInfo(strMsgTitle, strMsgDetail, iMsgType, accountId, strMsgId=""):
    objNewMsg = classMessageData()
    if len(strMsgId) <= 0:
        objNewMsg.strMsgId = str(uuid.uuid1())
    else:
        objNewMsg.strMsgId = strMsgId
    objNewMsg.iMsgTime = timeHelp.getNow()
    objNewMsg.strMsgTitle = strMsgTitle
    objNewMsg.strMsgDetail = strMsgDetail
    objNewMsg.iMsgType = iMsgType
    objNewMsg.strSendFrom = accountId

    return objNewMsg


@token_required
@permission_required('公告管理')
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """
    更新公告消息
    """
    objRsp = cResp()
    strMsgTitle = dict_param.get("title", "")
    strMsgDetail = dict_param.get("detail", "")
    iBroadcast = dict_param.get('broadcast', 0)
    strMsgId = dict_param.get("msgId", "")

    objNotice = yield from classDataBaseMgr.getInstance().getOneMsg(1, strMsgId)

    if objNotice is None:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    if strMsgTitle:
        objNotice.strMsgTitle = strMsgTitle
    if iBroadcast:
        objNotice.iBroadcast = iBroadcast
    if strMsgDetail:
        objNotice.strMsgDetail = strMsgDetail

    yield from classDataBaseMgr.getInstance().setNoticMsg(strMsgId, objNotice)
    # 构造回包
    yield from asyncio.sleep(1)

    MsgDataList, count = yield from classSqlBaseMgr.getInstance().getMsg(1, 1, 10)
    objRsp.data=MsgDataList
    objRsp.count=count
    fileName = __name__
    nameList = fileName.split('.')
    methodName = nameList.pop()
    # 日志
    dictActionBill = {
        'billType': 'adminActionBill',
        'accountId': dict_param.get('accountId', ''),
        'action': "修改公告消息",
        'actionTime': timeHelp.getNow(),
        'actionMethod': methodName,
        'actionDetail': "修改公告消息Id：{}".format(strMsgId),
        'actionIp': dict_param.get('srcIp', ''),
    }
    logging.getLogger('bill').info(json.dumps(dictActionBill))
    return classJsonDump.dumps(objRsp)
