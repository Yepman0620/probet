import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr



class cData():
    def __init__(self):
        self.MsgList = []


class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = ""


@asyncio.coroutine
def handleHttp(dict_param: dict):
    """
    手机端获取公告消息
    """
    objRsp = cResp()

    iType = int(dict_param.get("type", 1))
    MsgDataList = yield from classDataBaseMgr.getInstance().getAllMsg(iType)

    # 构造回包
    objRsp.data = cData()
    objRsp.data.MsgList = MsgDataList

    return classJsonDump.dumps(objRsp)






