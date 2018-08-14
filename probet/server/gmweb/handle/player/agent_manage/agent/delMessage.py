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
    """删除代理消息"""

    msgId = dict_param.get("msgId", "")
    if not msgId:
        raise exceptionLogic(errorLogic.client_param_invalid)

    # yield from classDataBaseMgr.getInstance().delSystemMsg(strMsgId)
    yield from classSqlBaseMgr.getInstance().delUserMsg(msgId)



