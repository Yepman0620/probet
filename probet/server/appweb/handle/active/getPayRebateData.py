import asyncio
from lib.jsonhelp import classJsonDump
from error.errorCode import exceptionLogic,errorLogic
from datawrapper.dataBaseMgr import classDataBaseMgr
from logic.enum.enumActive import enumActiveType,enumActiveState
from config.activeConfig import activeConfig_cfg
from lib.timehelp import timeHelp
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from appweb.logic.active import checkActiveData
from lib.tool import user_token_required

class cData():
    def __init__(self):
        self.iCurrentValidWater = 0
        self.iCurrentPayCoin = 0
        self.iLeftSeconds = 0
        self.iActiveStatus = 0
        self.iJoinActiveCoin = 0    #参与哪个奖励
        self.iActiveId = 0          #参与哪个奖励

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

    objActiveTypeItem = objActiveData.getTypeItemByType(enumActiveType.activePayRebate)
    if objActiveTypeItem is None:
        raise exceptionLogic(errorLogic.active_not_find)

    objResp.data = yield from getPayRebate(strAccountId, objActiveData, objActiveTypeItem)

    return classJsonDump.dumps(objResp)

@asyncio.coroutine
def getPayRebate(strAccountId ,objActiveData, objActiveTypeItem):
    objData = cData()

    objActiveItem = objActiveData.getItemByTypeId(enumActiveType.activePayRebate)

    if objActiveItem is None:
        # 还没有此类型的领取活动
        objData.iCurrentPayCoin = objActiveTypeItem.dictParam.get("activePayCoin",0)
        objData.iActiveStatus = enumActiveState.stateGet
        # 如果activepaytime 还没有 lefttime = 0
        iLeftTime = (24 * 3600 - (timeHelp.getNow() - objActiveTypeItem.dictParam.get("activePayTime",0)))
        if iLeftTime < 0:
            iLeftTime = 0
        objData.iLeftSeconds = iLeftTime

        objData.iActiveId = getActiveId(objData.iCurrentPayCoin)

    else:

        validWater = yield from classSqlBaseMgr.getInstance().getValidWaterByTimeRange(objActiveItem.iActiveTime,
                                                                                       timeHelp.getNow(),
                                                                                       strAccountId)

        pingboValidWater = yield from classSqlBaseMgr.getInstance().getAccountPinboHistoryValidWater(
            objActiveItem.iActiveTime, timeHelp.getNow(), strAccountId)

        objData.iCurrentValidWater = validWater + pingboValidWater
        objData.iJoinActiveCoin = activeConfig_cfg.get(str(objActiveItem.iActiveId), {}).get("taskConditionParam2", 0)
        objData.iActiveStatus = enumActiveState.stateAward#objActiveItem.iActiveState

    return objData


def getActiveId(payCoin):
    #hard code the vip level
    #TODO modify with config excel
    if payCoin > 0 and payCoin < 100:
        return 0
    elif payCoin >= 100 and payCoin < 500:
        return 1001
    elif payCoin >= 500 and payCoin < 1000:
        return 1002
    elif payCoin >= 1000 and payCoin < 5000:
        return 1003
    elif payCoin >= 5000 and payCoin < 50000:
        return 1004
    elif payCoin >= 50000:
        return 1005
    else:
        return 0
