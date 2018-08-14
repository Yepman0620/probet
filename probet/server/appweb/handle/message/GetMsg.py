import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic


class cData():
    def __init__(self):
        self.MsgList = []
        self.Count = 0


class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = ""


@asyncio.coroutine
def handleHttp(dict_param: dict):
    """
    获取消息
    """
    objRsp = cResp()

    iPageNum = int(dict_param.get("pageNum", 1))
    iType = int(dict_param.get("type", 0))
    if not all([iType, iPageNum]):
        raise exceptionLogic(errorLogic.client_param_invalid)

    if iPageNum <= 0:
        raise exceptionLogic(errorLogic.client_param_invalid)

    MsgDataList, count = yield from classSqlBaseMgr.getInstance().getMsg(iType, iPageNum, 10)

    # 构造回包
    objRsp.data = cData()
    objRsp.data.MsgList = MsgDataList
    objRsp.data.Count = count

    return classJsonDump.dumps(objRsp)






