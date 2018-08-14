from lib.observer import classObserver
from datawrapper.dataBaseMgr import classDataBaseMgr
from logic.enum.enumActive import enumActiveType,enumActiveState
from lib.timehelp import timeHelp
import asyncio
import logging

#activePayRebate 的支付回调
class classPaySuccessForRebateActive(classObserver):
    def __init__(self,eventName):
        super(classPaySuccessForRebateActive, self).__init__(eventName)

    @asyncio.coroutine
    def update(self, *args,**kwargs):
        if len(args) <= 0:
            logging.error("[{}] event args is null".format(self.eventName))
            return

        #第一个拿用户数据
        objPlayerData = kwargs["playerData"]
        iPayCoin = kwargs["payCoin"]
        iOrderTime = kwargs["orderTime"]
        
        objActiveData,objActiveLock = yield from classDataBaseMgr.getInstance().getActiveDataByLock(objPlayerData.strAccountId)
        if objActiveData is None:
            return

        # 检查 首冲返利活动
        objActiveTypeItem = objActiveData.getTypeItemByType(enumActiveType.activePayRebate)
        if objActiveTypeItem is not None:
            self.updateActive(objPlayerData,iPayCoin,iOrderTime,objActiveTypeItem)

        # 检查 vip 首冲返利活动
        objActiveTypeItem = objActiveData.getTypeItemByType(enumActiveType.activeVipPayRebate)
        if objActiveTypeItem is not None:
            self.updateActive(objPlayerData, iPayCoin, iOrderTime, objActiveTypeItem)


        yield from classDataBaseMgr.getInstance().setActiveDataByLock(objActiveData,objActiveLock)



    def updateActive(self,objPlayerData,iPayCoin,iOrderTime,objActiveTypeItem):

        if objActiveTypeItem is None:
            logging.error("accountId[{}] not have the payRebate active".format(objPlayerData.strAccountId))
            return
        if objActiveTypeItem.iActiveState > enumActiveState.stateGet:
            # 活动已经完成，pass
            return

        # 获取上一次充值，活动充值的时间
        iLastActivePayTime = objActiveTypeItem.dictParam.get("activePayNum", 0)
        if iLastActivePayTime == 0:
            # 上一次没有充值过
            objActiveTypeItem.dictParam["activePayTime"] = iOrderTime
            if "activePayCoin" in objActiveTypeItem.dictParam:
                objActiveTypeItem.dictParam["activePayCoin"] += iPayCoin
            else:
                objActiveTypeItem.dictParam["activePayCoin"] = iPayCoin
        else:
            # 查看活动充值是否已经超过24小时
            if (timeHelp.getNow() - iLastActivePayTime) > 24 * 3600:
                objActiveTypeItem.dictParam["activePayTime"] = iOrderTime
                objActiveTypeItem.dictParam["activePayCoin"] = iPayCoin
            else:
                if "activePayCoin" in objActiveTypeItem.dictParam:
                    objActiveTypeItem.dictParam["activePayCoin"] += iPayCoin
                else:
                    objActiveTypeItem.dictParam["activePayCoin"] = iPayCoin