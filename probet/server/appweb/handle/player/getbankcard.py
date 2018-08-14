import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib import certifytoken, constants
from lib.tool import user_token_required


class cData():
    def __init__(self):
        self.arrayCardNum = []
        self.iCoin = 0
        self.bankType = []


class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """银行卡入口"""

    objRsp = cResp()

    strAccountId = dict_param.get("accountId", "")
    objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(strAccountId)

    # 构造回包
    objRsp.data = cData()
    objRsp.data.arrayCardNum = objPlayerData.arrayBankCard
    objRsp.data.iCoin = "%.2f"%round(objPlayerData.iCoin/100, 2)
    objRsp.data.bankType.extend(constants.BANK_LIST)
    return classJsonDump.dumps(objRsp)