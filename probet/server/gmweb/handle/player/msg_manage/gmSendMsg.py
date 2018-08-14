import asyncio
import json
import logging
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from logic.data.userData import classMessageData
from lib.timehelp import timeHelp
import uuid
from gmweb.utils.tools import token_required, permission_required


class getMsgType(object):
    """发布的消息类型"""
    getNoticeType = 1     # 公告
    getNewsType = 2       # 新闻


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
@permission_required('新闻管理')
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """
    后台添加新闻公告系统消息
    """
    objRsp = cResp()
    strAccountId = dict_param.get('accountId')
    iMsgType = int(dict_param.get("type", 0))
    strMsgTitle = dict_param.get("title", "")
    strMsgDetail = dict_param.get("detail", "")
    strMsgId = dict_param.get("msgId", "")
    if not all([iMsgType, strMsgTitle, strMsgDetail]):
        raise exceptionLogic(errorLogic.client_param_invalid)

    if iMsgType == getMsgType.getNoticeType:

        iBroadcast = int(dict_param.get("broadcast", 0))

        objNewMsg = addMsgInfo(strMsgTitle, strMsgDetail, iMsgType, strAccountId, strMsgId)
        objNewMsg.iBroadcast = iBroadcast
        yield from classDataBaseMgr.getInstance().addMsg(iMsgType, objNewMsg, strMsgId)
        # 构造回包
        objRsp.data = cData(objNewMsg.strMsgId, objNewMsg.strMsgTitle, objNewMsg.strMsgDetail, objNewMsg.iMsgTime,
                            iMsgType)
        objRsp.data.iBroadcast = iBroadcast
        yield from asyncio.sleep(1)
        return classJsonDump.dumps(objRsp)

    elif iMsgType == getMsgType.getNewsType:
        objNewMsg = addMsgInfo(strMsgTitle, strMsgDetail, iMsgType, strAccountId, strMsgId)
        yield from classDataBaseMgr.getInstance().addMsg(iMsgType, objNewMsg, strMsgId)
        # 构造回包
        objRsp.data = cData(objNewMsg.strMsgId, objNewMsg.strMsgTitle, objNewMsg.strMsgDetail, objNewMsg.iMsgTime,
                            iMsgType)

        yield from asyncio.sleep(1)
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': dict_param.get('accountId', ''),
            'action': "发送新闻公告",
            'actionTime': timeHelp.getNow(),
            'actionMethod': methodName,
            'actionDetail': "发送新闻公告Id：{},标题：{}".format(strMsgId,strMsgTitle),
            'actionIp': dict_param.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(objRsp)

    else:
        logging.error("unknown msg type [{}]".format(iMsgType))
        raise exceptionLogic(errorLogic.client_param_invalid)



































