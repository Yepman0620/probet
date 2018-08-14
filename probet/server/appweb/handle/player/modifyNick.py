import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib import certifytoken
from lib.tool import user_token_required


class cData():
    def __init__(self):
        self.nick = ""


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """修改昵称"""
    objRsp = cResp()

    strAccountId = dict_param.get("accountId", "")
    strNick = dict_param.get("nick", "")
    if not strNick:
        raise exceptionLogic(errorLogic.client_param_invalid)
    objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)

    objPlayerData.strNick = strNick
    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)

    # 构造回包
    objRsp.data = cData()
    objRsp.data.nick = objPlayerData.strNick

    return classJsonDump.dumps(objRsp)











