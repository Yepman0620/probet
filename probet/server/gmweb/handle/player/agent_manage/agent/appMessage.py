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

    msgDataList = yield from classSqlBaseMgr.getInstance().appGetAgentMsg(agentId)
    unReadNum = yield from classSqlBaseMgr.getInstance().getAgentMsgUnReadNum(agentId)
    x = [msgDataList[(i-1):(i+1)] for i in range(1,len(msgDataList)+1) if i%2==1]

    # 构造回包
    objRsp.data = cData()
    objRsp.data.MsgDataList = x
    objRsp.data.unReadNum = unReadNum
    return classJsonDump.dumps(objRsp)
