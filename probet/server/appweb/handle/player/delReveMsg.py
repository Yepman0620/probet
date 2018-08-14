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
    """删除收件箱消息"""

    strMsgId = dict_param.get("msgId", "")
    if not strMsgId:
        raise exceptionLogic(errorLogic.client_param_invalid)
    # yield from classDataBaseMgr.getInstance().delSystemMsg(strMsgId)
    yield from classSqlBaseMgr.getInstance().delUserMsg(strMsgId)


















