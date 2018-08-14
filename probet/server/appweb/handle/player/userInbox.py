import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib import certifytoken
from lib.timehelp import timeHelp
from lib.tool import user_token_required


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


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """收件箱"""
    objRsp = cResp()

    strAccountId = dict_param.get("accountId", "")
    iPageNum = int(dict_param.get("pageNum", 1))
    if not iPageNum:
        raise exceptionLogic(errorLogic.client_param_invalid)

    MsgDataList, count = yield from classSqlBaseMgr.getInstance().getSysMsg(strAccountId, iPageNum, 10)
    unReadNum= yield from classSqlBaseMgr.getInstance().getSysMsgUnReadNum(strAccountId)

    # 构造回包
    objRsp.data = cData()
    objRsp.data.MsgDataList = MsgDataList
    objRsp.data.MsgCount = count
    objRsp.data.unReadNum = unReadNum
    return classJsonDump.dumps(objRsp)
