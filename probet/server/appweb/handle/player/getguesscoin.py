import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib import certifytoken
from lib.tool import user_token_required


class cData():
    def __init__(self):
        self.iguessCoin = 0


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """刷新电竞钱包"""
    objRsp = cResp()

    strAccountId = dict_param.get("accountId", "")

    if len(strAccountId) <= 0:
        objRsp.data = cData()
        objRsp.data.iguessCoin = "0.00"
        return classJsonDump.dumps(objRsp)
    objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(strAccountId)

    # 构造回包
    objRsp.data = cData()
    objRsp.data.iguessCoin = "%.2f" % round(objPlayerData.iGuessCoin/100, 2)

    return classJsonDump.dumps(objRsp)