import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib.tool import agent_token_required
from lib.timehelp import timeHelp



class cData():
    def __init__(self):
        self.MsgDataList = []
        self.MsgCount = 0
        self.unReadNum = 0


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@agent_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """代理的系统消息"""
    objRsp = cResp()

    agentId = dict_param.get("agentId", "")
    page = int(dict_param.get("pn", 1))
    if not page:
        raise exceptionLogic(errorLogic.client_param_invalid)

    MsgDataList, count = yield from classSqlBaseMgr.getInstance().getAgentMsg(agentId, page, 10)
    unReadNum= yield from classSqlBaseMgr.getInstance().getAgentMsgUnReadNum(agentId)

    # 构造回包
    objRsp.data = cData()
    objRsp.data.MsgDataList = MsgDataList
    objRsp.data.MsgCount = count
    objRsp.data.unReadNum = unReadNum
    return classJsonDump.dumps(objRsp)
