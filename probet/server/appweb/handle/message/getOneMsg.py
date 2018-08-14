import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic


class cData():
    def __init__(self):
        self.Msg = ""

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@asyncio.coroutine
def handleHttp(dict_param: dict):
    """
    获取指定消息
    """
    objRsp = cResp()

    strMsgId = dict_param.get("msgId", "")
    iType = dict_param.get("type", 0)
    if not strMsgId:
        raise exceptionLogic(errorLogic.client_param_invalid)

    MsgData = yield from classDataBaseMgr.getInstance().getOneMsg(iType, strMsgId)
    if MsgData is None:
        return classJsonDump.dumps(objRsp)
    # 构造回包
    objRsp.data = cData()
    objRsp.data.Msg = MsgData
    return classJsonDump.dumps(objRsp)




