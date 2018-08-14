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
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.db_tools import session
from gmweb.utils.models import UserInfo


class cData():
    def __init__(self, iMsgId, strMsgTitle, strMsgDetail, iMsgTime):
        self.msgId = iMsgId
        self.title = strMsgTitle
        self.detail = strMsgDetail
        self.msgTime = iMsgTime
        self.readFlag = 0
        # self.unReadNum = 0


class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = ""


def addMsgInfo(MsgId,strMsgTitle, strMsgDetail, sendTo, sendFrom):
    objNewMsg = classMessageData()
    objNewMsg.strMsgId = MsgId
    objNewMsg.iMsgTime = timeHelp.getNow()
    objNewMsg.strMsgTitle = strMsgTitle
    objNewMsg.strMsgDetail = strMsgDetail
    objNewMsg.strAccountId = sendTo
    objNewMsg.strSendFrom = sendFrom
    objNewMsg.iReadFlag = 0

    return objNewMsg


@token_required
@permission_required('系统消息发送')
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """
    后台添加系统消息
    """
    objRsp = cResp()

    sendTo = dict_param.get("userIds", "")
    strMsgTitle = dict_param.get("msgTitle", "")
    strMsgDetail = dict_param.get("msgDetail", "")
    AccountId = dict_param.get("accountId", "")
    if not all([strMsgTitle, strMsgDetail]):
        raise exceptionLogic(errorLogic.client_param_invalid)

    MsgId = str(uuid.uuid1())
    if sendTo:
        userIds = sendTo.split(',')
        for userId in userIds:
            objNewMsg = addMsgInfo(MsgId,strMsgTitle, strMsgDetail, userId, AccountId)
            yield from classDataBaseMgr.getInstance().addSystemMsg(objNewMsg)

    else:
        sql = "select dj_account.accountId from dj_account"
        result = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
        if result.rowcount <= 0:
            logging.info(" 没有账户 ")
        else:
            for var_row in result:
                userId = var_row.accountId
                objNewMsg = addMsgInfo(MsgId,strMsgTitle, strMsgDetail, userId, AccountId)
                yield from classDataBaseMgr.getInstance().addSystemMsg(objNewMsg)
    fileName = __name__
    nameList = fileName.split('.')
    methodName = nameList.pop()
    # 日志
    dictActionBill = {
        'billType': 'adminActionBill',
        'accountId': dict_param.get('accountId', ''),
        'action': "发送系统消息",
        'actionTime': timeHelp.getNow(),
        'actionMethod': methodName,
        'actionDetail': "新增新闻公告标题：{},Id：{}".format(strMsgTitle,MsgId),
        'actionIp': dict_param.get('srcIp', ''),
    }
    logging.getLogger('bill').info(json.dumps(dictActionBill))

    return classJsonDump.dumps(objRsp)

