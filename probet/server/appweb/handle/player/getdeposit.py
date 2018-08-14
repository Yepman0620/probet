import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from logic.data.userData import classUserData
from lib import certifytoken, constants
from lib.tool import user_token_required


class cData():
    def __init__(self):
        self.iCoreCoin = 0
        self.iGuessCoin = 0
        self.payType = []
        self.thirdPayGrade = []

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """取款入口"""

    objRsp = cResp()
    strAccountId = dict_param.get("accountId", "")
    objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(strAccountId)

    # 构造回包
    objRsp.data = cData()
    objRsp.data.iCoreCoin = "%.2f"%round(objPlayerData.iCoin/100,2)
    objRsp.data.iGuessCoin = "%.2f"%round(objPlayerData.iGuessCoin/100,2)

    objRsp.data.payType.extend(constants.DEPOSIT_LIST)
    objRsp.data.thirdPayGrade.extend(constants.THIRD_PAY_GRADE)

    return classJsonDump.dumps(objRsp)

