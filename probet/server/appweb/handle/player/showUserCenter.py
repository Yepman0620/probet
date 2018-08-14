import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib import certifytoken
from config.vipConfig import vip_config
from lib.tool import user_token_required


class cData():
    def __init__(self):
        self.accountId = ""
        self.coin = ""
        self.headAddress = ""
        self.phoneNum = ""
        self.email = ""
        self.bankCard = []
        self.tradePwd = 0



class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """个人中心入口"""
    objRsp = cResp()

    strAccountId = dict_param.get("accountId", "")
    objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(strAccountId)
    payMonthly, orderTime = yield from classSqlBaseMgr.getInstance().getAccountFirstPayByDay(strAccountId)
    validWaterMonthly = yield from classSqlBaseMgr.getInstance().getValidWaterMonthly(strAccountId)
    if orderTime:
        # surplusTime = orderTime+86400 - timeHelp.getNow()
        endTime = orderTime+86400
    else:
        # surplusTime = 0
        endTime = 0

    # 构造回包
    objRsp.data = cData()
    objRsp.data.accountId = objPlayerData.strAccountId
    objRsp.data.coin = "%.2f"%round(objPlayerData.iCoin/100, 2)
    objRsp.data.headAddress = objPlayerData.strHeadAddress
    objRsp.data.phoneNum = objPlayerData.strPhone
    objRsp.data.realName = objPlayerData.strRealName
    objRsp.data.sex = objPlayerData.strSex
    objRsp.data.born = objPlayerData.strBorn
    objRsp.data.address = objPlayerData.dictAddress
    objRsp.data.email = objPlayerData.strEmail
    objRsp.data.bankCard = objPlayerData.arrayBankCard
    objRsp.data.level = objPlayerData.iLevel
    objRsp.data.levelValidWater = "%.2f" % round(objPlayerData.iLevelValidWater/100, 2)
    objRsp.data.paymonthly = "%.2f" % round(payMonthly/100, 2)
    objRsp.data.validWaterMonthly = "%.2f" % round(validWaterMonthly/100, 2)
    objRsp.data.endTime = endTime
    for var_value in vip_config.values():
        if var_value['level'] == objPlayerData.iLevel:
            objRsp.data.upGradeValidWater = "%.2f" % round(var_value['upGradeValidWater']/100, 2)
            objRsp.data.keepValidWater = "%.2f" % round(var_value['keepValidWater']/100, 2)
    if objPlayerData.strTradePassword:
        objRsp.data.tradePwd = 1  # 表示已经设置了交易密码
    else:
        objRsp.data.tradePwd = 0  # 表示没有设置交易密码

    return classJsonDump.dumps(objRsp)

































