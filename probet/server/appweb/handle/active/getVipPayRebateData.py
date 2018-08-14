import asyncio
from lib.jsonhelp import classJsonDump
from error.errorCode import exceptionLogic,errorLogic
from datawrapper.dataBaseMgr import classDataBaseMgr
from logic.enum.enumActive import enumActiveType,enumActiveState
from config.activeConfig import activeConfig_cfg
from lib import certifytoken
from lib.timehelp import timeHelp
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from appweb.logic.active import checkActiveData
from lib.tool import user_token_required

class cData():
    def __init__(self):
        self.iCurrentVipLevel = 0
        self.iCurrentMonthValidWater = 0
        self.iCurrentValidWater = 0
        self.iCurrentPayCoin = 0
        self.iLeftSeconds = 0
        self.iActiveStatus = 0
        self.iActiveId = 0


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = cData()

@user_token_required
@asyncio.coroutine
def handleHttp(dictParam: dict):
    objResp = cResp()
    strAccountId = dictParam.get('accountId','')

    yield from checkActiveData(strAccountId)

    objActiveData, objActiveLock = yield from classDataBaseMgr.getInstance().getActiveDataByLock(strAccountId)
    if objActiveData is None:
        raise exceptionLogic(errorLogic.active_not_find)

    objActiveTypeItem = objActiveData.getTypeItemByType(enumActiveType.activeVipPayRebate)
    if objActiveTypeItem is None:
        raise exceptionLogic(errorLogic.active_not_find)

    objResp.data = yield from getVipPayRebate(strAccountId, objActiveData, objActiveTypeItem)

    return classJsonDump.dumps(objResp)

@asyncio.coroutine
def getVipPayRebate( strAccountId ,objActiveData, objActiveTypeItem):
    objData = cData()

    objActiveItem = objActiveData.getItemByTypeId(enumActiveType.activeVipPayRebate)
    objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(strAccountId)
    if objPlayerData is None:
        raise exceptionLogic(errorLogic.player_data_not_found)

    objData.iCurrentVipLevel = objPlayerData.iLevel
    #跟进vip 等级 计算  iActiveId
    objData.iActiveId = getVipActiveId(objPlayerData.iLevel)

    if objActiveItem is None:
        # 还没有此类型的领取活动
        objData.iCurrentPayCoin = objActiveTypeItem.dictParam.get("activePayCoin",0)
        objData.iActiveStatus = enumActiveState.stateGet
        # 如果activepaytime 还没有 lefttime = 0
        iLeftTime = (24 * 3600 - (timeHelp.getNow() - objActiveTypeItem.dictParam.get("activePayTime",0)))
        if iLeftTime < 0:
            iLeftTime = 0
        objData.iLeftSeconds = iLeftTime

    else:

        #活动开始到现在有效流水
        validWater = yield from classSqlBaseMgr.getInstance().getValidWaterByTimeRange(objActiveItem.iActiveTime,
                                                                                       timeHelp.getNow(),
                                                                                       strAccountId)

        pingboValidWater = yield from classSqlBaseMgr.getInstance().getAccountPinboHistoryValidWater(
            objActiveItem.iActiveTime, timeHelp.getNow(), strAccountId)

        objData.iCurrentValidWater = validWater + pingboValidWater

        #当月的流水
        iLastStartTs = timeHelp.lastMonthStartTimestamp()
        iNowStartTs = timeHelp.monthStartTimestamp()
        pinboMonthValidWater = yield from classSqlBaseMgr.getInstance().getOnePinboHistoryValidWater(strAccountId, iLastStartTs, iNowStartTs)
        monthValidWater = yield from classSqlBaseMgr.getInstance().getValidWaterMonthly(strAccountId)
        objData.iCurrentMonthValidWater = pinboMonthValidWater + monthValidWater
        objData.iActiveStatus = enumActiveState.stateAward


    return objData

def getVipActiveId(iVipLevel):
    #hard code the vip level
    if iVipLevel == 0:
        return 0
    elif iVipLevel == 1:
        return 2001
    elif iVipLevel == 2:
        return 2002
    elif iVipLevel == 3:
        return 2003
    elif iVipLevel == 4:
        return 2004
    else:
        return 0
