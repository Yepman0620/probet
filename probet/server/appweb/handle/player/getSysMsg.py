import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib import certifytoken
from lib.tool import user_token_required


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """
    获取指定消息
    """
    objRsp = cResp()

    strAccountId = dict_param.get("accountId", "")
    strMsgId = dict_param.get("msgId", "")
    if not strMsgId:
        raise exceptionLogic(errorLogic.client_param_invalid)
    yield from classSqlBaseMgr.getInstance().changeReadFlag(strMsgId)
    MsgData = yield from classDataBaseMgr.getInstance().getOneSystemMsg(strMsgId, strAccountId)
    if MsgData:
        sysMsgData = {}
        sysMsgData['msgTime'] = MsgData.iMsgTime
        sysMsgData['msgTitle'] = MsgData.strMsgTitle
        sysMsgData['msgDetail'] = MsgData.strMsgDetail
        sysMsgData['readFlag'] = MsgData.iReadFlag
        sysMsgData['msgId'] = MsgData.strMsgId
    else:
        sysMsgData = MsgData

    # 构造回包
    objRsp.data = sysMsgData
    return classJsonDump.dumps(objRsp)




