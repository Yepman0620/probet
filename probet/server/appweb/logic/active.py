import asyncio
import logging
from logic.data.userData import classActiveData,classActiveItem,classActiveTypeItem
from config.activeConfig import activeConfig_cfg
from logic.enum.enumActive import enumActiveType,enumActiveStartType,enumActiveState,enumActiveExpireType,enumActiveRefreshType
from lib.timehelp import timeHelp
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic,errorLogic
from datawrapper.playerDataOpWrapper import addPlayerBill
from logic.enum.enumCoinOp import CoinOp

g_activeTypeIdCfg = []
for var_value in activeConfig_cfg.values():
    g_activeTypeIdCfg.append(var_value["taskType"])

#获取所有活动类型，对应enumActiveType
g_activeTypeIdCfg = list(set(g_activeTypeIdCfg))

@asyncio.coroutine
def initActiveData(strAccountId):
    # 初始化 活动数据
    objActiveData = yield from classDataBaseMgr.getInstance().getActiveData(strAccountId)
    if objActiveData is not None:
        # raise exceptionLogic(errorLogic.active_already_exist)
        logging.error("account[{}] active data already exist".format(strAccountId))
        return

    objNewActiveData = classActiveData()
    objNewActiveData.strAccountId = strAccountId

    iNowTime = timeHelp.getNow()
    for var_cfg in activeConfig_cfg.values():
        if (var_cfg["actStartTime"] < iNowTime) and (iNowTime < var_cfg["actEndTime"]):
            #在活动有效时间内
            if var_cfg["getTaskCondition"] == enumActiveStartType.startRegist:
                objNewActiveItem = classActiveItem()
                objNewActiveItem.iActiveId = int(var_cfg['id'])
                # objNewActiveItem.iActiveTime = timeHelp.getNow()
                objNewActiveItem.iActiveTime = 0
                objNewActiveItem.iActiveState = enumActiveState.stateGet
                objNewActiveData.dictActiveItem[objNewActiveItem.iActiveId] = objNewActiveItem

    for var_active_type_id in g_activeTypeIdCfg:
        objNewActiveTypeItem = classActiveTypeItem()
        objNewActiveTypeItem.iActiveTypeId = var_active_type_id
        objNewActiveData.dictActiveTypeItem[var_active_type_id] = objNewActiveTypeItem

    yield from classDataBaseMgr.getInstance().setActiveDataByLock(objNewActiveData,"",False,True)

@asyncio.coroutine
def checkActiveData(strAccountId):

    objActiveData,objActiveLock = yield from classDataBaseMgr.getInstance().getActiveDataByLock(strAccountId)
    if objActiveData is None:
        #raise exceptionLogic(errorLogic.active_not_find)
        yield from initActiveData(strAccountId)
        return

    iNowTime = timeHelp.getNow()
    bIsFind = False
    for var_cfg in activeConfig_cfg.values():
        if (var_cfg["actStartTime"] < iNowTime) and (iNowTime < var_cfg["actEndTime"]):
            # 在活动有效时间内
            if var_cfg["getTaskCondition"] == enumActiveStartType.startRegist:
                if int(var_cfg['id']) not in objActiveData.dictActiveItem:
                    objNewActiveItem = classActiveItem()
                    objNewActiveItem.iActiveId = int(var_cfg['id'])
                    objNewActiveItem.iActiveTime = timeHelp.getNow()
                    objNewActiveItem.iActiveState = enumActiveState.stateGet
                    objActiveData.dictActiveItem[objNewActiveItem.iActiveId] = objNewActiveItem
                    bIsFind = True

    for var_active_type_id in g_activeTypeIdCfg:
        if var_active_type_id not in objActiveData.dictActiveTypeItem:
            objNewActiveTypeItem = classActiveTypeItem()
            objNewActiveTypeItem.iActiveTypeId = var_active_type_id
            objActiveData.dictActiveTypeItem[var_active_type_id] = objNewActiveTypeItem
            bIsFind = True

    #检查一下过期状态
    listExpireKey = []
    for var_key,var_item in objActiveData.dictActiveItem.items():
        var_cfg = activeConfig_cfg.get(str(var_item.iActiveId),None)
        if var_cfg is None:
            logging.error("active id [{}]".format(var_item.iActiveId))
            raise exceptionLogic(errorLogic.active_not_find)

        if var_cfg["taskExpireType"] == enumActiveExpireType.activeRefreshExpireNone:
            pass
        elif var_cfg["taskExpireType"] == enumActiveExpireType.activeRefreshExpireDay:
            if not timeHelp.isSameDay(iNowTime,var_item.iActiveTime):
                #每日过期
                listExpireKey.append(var_key)
                bIsFind = True
        else:
            pass

    #删除过期的活动
    for var_expire_key in listExpireKey:
        if var_expire_key in objActiveData.dictActiveItem.items():
            objActiveData.dictActiveItem.pop(var_expire_key)

    #检查一下更新:
    for var_key,var_item in objActiveData.dictActiveItem.items():
        var_cfg = activeConfig_cfg.get(str(var_item.iActiveId),None)
        if var_cfg is None:
            logging.error("active id [{}]".format(var_item.iActiveId))
            raise exceptionLogic(errorLogic.active_not_find)

        if var_cfg["taskRefreshType"] == enumActiveRefreshType.activeRefreshNone:
            pass
        elif var_cfg["taskRefreshType"] == enumActiveRefreshType.activeRefreshDay:
            if not timeHelp.isSameMonth(iNowTime,var_item.iActiveTime):
                #更新
                bIsFind = True
                var_item.iActiveState = enumActiveState.stateGet
                var_item.iActiveTime = iNowTime

        elif var_cfg["taskRefreshType"] == enumActiveRefreshType.activeRefreshWeek:
            if not timeHelp.isSameWeek(iNowTime,var_item.iActiveTime):
                if not timeHelp.isSameWeek(iNowTime, var_item.iActiveTime):
                    # 更新
                    bIsFind = True
                    var_item.iActiveState = enumActiveState.stateGet
                    var_item.iActiveTime = iNowTime
        elif var_cfg["taskRefreshType"] == enumActiveRefreshType.activeRefreshMonty:
            if not timeHelp.isSameMonth(iNowTime,var_item.iActiveTime):
                if not timeHelp.isSameMonth(iNowTime, var_item.iActiveTime):
                    # 更新
                    bIsFind = True
                    var_item.iActiveState = enumActiveState.stateGet
                    var_item.iActiveTime = iNowTime
        else:
            pass


    if bIsFind:
        yield from classDataBaseMgr.getInstance().setActiveDataByLock(objActiveData, objActiveLock)
    else:
        yield from classDataBaseMgr.getInstance().releaseActiveDataLock(strAccountId, objActiveLock)

@asyncio.coroutine
def joinOncePayRebateActive(strAccountId:str,iActiveId:int):

    var_cfg = activeConfig_cfg.get(str(iActiveId),None)
    if var_cfg is None:
        raise exceptionLogic(errorLogic.active_cfg_not_find)

    if var_cfg["taskType"] != enumActiveType.activePayRebate:
        raise exceptionLogic(errorLogic.active_cfg_not_find)

    objActiveData, objActiveLock = yield from classDataBaseMgr.getInstance().getActiveDataByLock(strAccountId,None)
    if objActiveData is None:
        yield from classDataBaseMgr.getInstance().releaseActiveDataLock(strAccountId, None)
        raise exceptionLogic(errorLogic.active_not_find)

    #检测是否重复参与
    checkHaveSameActiveType(objActiveData, enumActiveType.activePayRebate, var_cfg,strAccountId)
    objActiveTypeItem = objActiveData.getTypeItemByType(enumActiveType.activePayRebate)
    if objActiveTypeItem is None:
        raise exceptionLogic(errorLogic.active_not_find)

    #看看是否符合条件规则
    from appweb.handle.active.getPayRebateData import getActiveId

    iCheckActiveId = getActiveId(objActiveTypeItem.dictParam.get("activePayCoin", 0))
    if iActiveId != iCheckActiveId:
        raise exceptionLogic(errorLogic.active_requirements_not_met)

    iNowTime = timeHelp.getNow()

    if (var_cfg["actStartTime"] < iNowTime) and (iNowTime < var_cfg["actEndTime"]):
        objNewActiveItem = classActiveItem()
        objNewActiveItem.iActiveId = int(var_cfg['id'])
        objNewActiveItem.iActiveTime = timeHelp.getNow()
        objNewActiveItem.iActiveState = enumActiveState.stateAward
        objActiveData.dictActiveItem[objNewActiveItem.iActiveId] = objNewActiveItem

    else:
        raise exceptionLogic(errorLogic.active_time_not_valid)

    #给用户加钱
    objPlayerData,objPlayerLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
    if objPlayerData is None:
        raise exceptionLogic(errorLogic.player_data_not_found)

    #充值已经加过一倍流水了
    iAddCoin = int(var_cfg["awardNum"])
    objPlayerData.iCoin += iAddCoin
    iPayCoin = int(var_cfg["taskConditionParam2"])
    objPlayerData.iNotDrawingCoin += ((int(var_cfg["awardNum"])) * int(var_cfg["waterRate"]) + iPayCoin
                                      * int(var_cfg["waterRate"] - 1))

    yield from addPlayerBill(strAccountId, iAddCoin, objPlayerData.iCoin, CoinOp.coinOpActiveAward,tradeState=1,
                             strDes="首冲奖励活动 冲[{}] 奖励[{}]".format(iPayCoin,iAddCoin))

    yield from classDataBaseMgr.getInstance().setActiveDataByLock(objActiveData, objActiveLock)
    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerLock)


@asyncio.coroutine
def joinVipPayRebateActive(strAccountId:str,iActiveId:int):
    var_cfg = activeConfig_cfg.get(str(iActiveId),None)
    if var_cfg is None:
        raise exceptionLogic(errorLogic.active_cfg_not_find)

    if var_cfg["taskType"] != enumActiveType.activeVipPayRebate:
        raise exceptionLogic(errorLogic.active_cfg_not_find)

    objActiveData, objActiveLock = yield from classDataBaseMgr.getInstance().getActiveDataByLock(strAccountId,None)
    if objActiveData is None:
        yield from classDataBaseMgr.getInstance().releaseActiveDataLock(strAccountId, None)
        raise exceptionLogic(errorLogic.active_not_find)

    objActiveTypeItem = objActiveData.getTypeItemByType(enumActiveType.activeVipPayRebate)
    if objActiveTypeItem is None:
        raise exceptionLogic(errorLogic.active_not_find)

    #检测是否重复参与
    checkHaveSameActiveType(objActiveData,enumActiveType.activeVipPayRebate,var_cfg,strAccountId)

    # 看看是否符合条件规则
    from appweb.handle.active.getVipPayRebateData import getVipActiveId

    # 查看等级是否有效
    objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(strAccountId)
    iCheckActiveId = getVipActiveId(objPlayerData.iLevel)
    if iActiveId != iCheckActiveId:
        raise exceptionLogic(errorLogic.active_requirements_not_met)

    #查看总充值是否有效
    #HARD code
    if objActiveTypeItem.dictParam.get("activePayCoin", 0) < 10000:
        raise exceptionLogic(errorLogic.active_requirements_not_met)

    iNowTime = timeHelp.getNow()

    if (var_cfg["actStartTime"]) < iNowTime and (iNowTime < var_cfg["actEndTime"]):
        objNewActiveItem = classActiveItem()
        objNewActiveItem.iActiveId = int(var_cfg['id'])
        objNewActiveItem.iActiveTime = timeHelp.getNow()
        objNewActiveItem.iActiveState = enumActiveState.stateAward
        objActiveData.dictActiveItem[objNewActiveItem.iActiveId] = objNewActiveItem

    else:
        raise exceptionLogic(errorLogic.active_time_not_valid)

    # 给用户加钱
    objPlayerData, objPlayerLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
    if objPlayerData is None:
        raise exceptionLogic(errorLogic.player_data_not_found)

    # 充值已经加过一倍流水了
    iAddCoin = int(var_cfg["awardNum"])
    objPlayerData.iCoin += iAddCoin
    iPayCoin = int(var_cfg["taskConditionParam2"])
    objPlayerData.iNotDrawingCoin += ((int(var_cfg["awardNum"])) * int(var_cfg["waterRate"]) + iPayCoin
                                      * int(var_cfg["waterRate"] - 1))

    yield from addPlayerBill(strAccountId, iAddCoin, objPlayerData.iCoin, CoinOp.coinOpActiveAward, tradeState=1,
                             strDes="vip 每月首冲奖励活动 冲[{}] 奖励[{}]".format(iPayCoin, iAddCoin))

    yield from classDataBaseMgr.getInstance().setActiveDataByLock(objActiveData, objActiveLock)

    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerLock)


def checkHaveSameActiveType(objActiveData,activeType,activeCfg,strAccountId):
    # 检测是否重复参与
    for var_key, var_item in objActiveData.dictActiveItem.items():
        temp_var_cfg = activeConfig_cfg.get(str(var_key), None)
        if temp_var_cfg is None:
            yield from classDataBaseMgr.getInstance().releaseActiveDataLock(strAccountId, None)
            raise exceptionLogic(errorLogic.active_cfg_not_find)

        if activeCfg["taskType"] == activeType:#enumActiveType.activePayRebate:
            yield from classDataBaseMgr.getInstance().releaseActiveDataLock(strAccountId, None)
            raise exceptionLogic(errorLogic.active_have_already_get)


