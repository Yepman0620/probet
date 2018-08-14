import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib.tool import agent_token_required


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@agent_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """
    消息详情
    """
    objRsp = cResp()

    agentId = dict_param.get("agentId", "")
    msgId = dict_param.get("msgId", "")
    if not msgId:
        raise exceptionLogic(errorLogic.client_param_invalid)

    yield from classSqlBaseMgr.getInstance().changeReadFlag(msgId)
    MsgData = yield from classDataBaseMgr.getInstance().getOneAgentMsg(msgId, agentId)
    if MsgData:
        agentMsgData = {}
        agentMsgData['msgTime'] = MsgData.iMsgTime
        agentMsgData['msgTitle'] = MsgData.strMsgTitle
        agentMsgData['msgDetail'] = MsgData.strMsgDetail
        agentMsgData['readFlag'] = MsgData.iReadFlag
        agentMsgData['msgId'] = MsgData.strMsgId
    else:
        agentMsgData = []

    # 构造回包
    objRsp.data = agentMsgData
    return classJsonDump.dumps(objRsp)




