import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib import certifytoken
from lib.constants import BANK_LIST
from lib.tool import user_token_required
from logic.regex import precompile

class cData():
    def __init__(self):
        self.arrayCardNum = []
        self.iCoin = 0


class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """添加银行卡"""
    objRsp = cResp()
    strAccountId = dict_param.get("accountId", "")

    strCardNum = str(dict_param.get("cardNum", ""))
    strRealName = dict_param.get("realName", "")
    strtBank = dict_param.get("bank", "")
    strCardAddress = dict_param.get("cardAddress", {})
    sCode = str(dict_param.get("iCode", ""))
    if not all([strCardNum, strRealName, strtBank, sCode]):
        raise exceptionLogic(errorLogic.client_param_invalid)

    objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
    if not objPlayerData.strPhone:
        raise exceptionLogic(errorLogic.player_telephone_is_not_bind)

    iCode = yield from classDataBaseMgr.getInstance().getPhoneVerify(objPlayerData.strPhone)
    if not iCode:
        raise exceptionLogic(errorLogic.verify_code_expired)
    if iCode != sCode:
        raise exceptionLogic(errorLogic.verify_code_not_valid)
    else:
        yield from classDataBaseMgr.getInstance().delPhoneVerify(objPlayerData.strPhone)
        if len(objPlayerData.arrayBankCard) >= 5:
            raise exceptionLogic(errorLogic.player_bankcard_max_limit)
        for bank in BANK_LIST:
            if strtBank in list(bank.values()):
                cardData = {}
                cardData["cardNum"] = strCardNum
                cardData["behindFourNum"] = strCardNum[-4:]
                cardData["holder"] = strRealName
                cardData["bank"] = bank
                cardData["bankAddress"] = strCardAddress
                objPlayerData.arrayBankCard.append(cardData)
                yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)

    # 构造回包
    objRsp.data = cData()
    objRsp.data.arrayCardNum = objPlayerData.arrayBankCard
    objRsp.data.iCoin = "%.2f"%round(objPlayerData.iCoin/100, 2)

    return classJsonDump.dumps(objRsp)






















