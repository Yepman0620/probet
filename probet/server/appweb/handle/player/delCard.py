import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib import certifytoken
import logging
from lib.tool import user_token_required


class cData():
    def __init__(self):
        self.bankCard = []


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """删除银行卡"""
    objRsp = cResp()

    strAccountId = dict_param.get("accountId", "")
    strCardNum = str(dict_param.get("cardNum", ""))
    if not strCardNum:
        raise exceptionLogic(errorLogic.client_param_invalid)
    objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
    for var in objPlayerData.arrayBankCard:
        ret = list(var.values())
        print(type(ret))
        if strCardNum in ret:
            try:
                objPlayerData.arrayBankCard.remove(var)
            except Exception as e:
                logging.exception(e)
    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)

    objRsp.data = cData()
    objRsp.data.BankCard = objPlayerData.arrayBankCard

    return classJsonDump.dumps(objRsp)









