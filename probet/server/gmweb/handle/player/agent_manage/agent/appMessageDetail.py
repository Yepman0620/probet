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
        self.data = []


@agent_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """
    app消息详情
    """
    objRsp = cResp()

    agentId = dict_param.get("agentId", "")

    with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
        sql_read = "update dj_all_msg set readFlag=1 where dj_all_msg.type=3 and sendTo=%s"
        yield from conn.execute(sql_read, [agentId])
        sql = "select msgTime,msgTitle,msgDetail,msgId,readFlag from dj_all_msg where sendTo=%s and dj_all_msg.type=3 order by msgTime desc limit 0,10"
        result = yield from conn.execute(sql, [agentId])
        if result.rowcount<=0:
            agentMsgList = []
        else:
            agentMsgList = []
            for var in result:
                agentMsgData = {}
                agentMsgData['msgTime'] = var.msgTime
                agentMsgData['msgTitle'] = var.msgTitle
                agentMsgData['msgDetail'] = var.msgDetail
                agentMsgData['readFlag'] = var.readFlag
                agentMsgData['msgId'] = var.msgId
                agentMsgList.append(agentMsgData)

    # 构造回包
    objRsp.data = agentMsgList
    return classJsonDump.dumps(objRsp)




