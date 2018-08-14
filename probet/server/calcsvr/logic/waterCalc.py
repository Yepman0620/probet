#from calcsvr.singleton import syncRedisMgr
from gmweb.handle.pinbo.check_pingbo_wagers import todo_pingbo_wagers
from gmweb.handle.pinbo.wagers import get_wagers
from lib.timehelp import timeHelp
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.playerDataOpWrapper import addPlayerBill
from lib.timehelp.timeHelp import getNow, timestamp2Str
from logic.enum.enumCoinOp import CoinOp
from config.vipConfig import vip_config
import asyncio
import logging
import uuid
from config.commissionConfig import commission_config
from datawrapper.agentDataOpWrapper import addCommissionBill,getDepositDrawingPoundage,getAgentConfig

@asyncio.coroutine
def runExecuteAll(beginTime,endTime):

    listAllRet = yield from classSqlBaseMgr.getInstance().getAllPinboHistoryValidWater(beginTime, endTime)
    return listAllRet

@asyncio.coroutine
def runExcuteOne(accountId,beginTime,endTime):
    iRet = yield from classSqlBaseMgr.getInstance().getOnePinboHistoryValidWater(accountId,beginTime,endTime)
    return iRet


#每天中午进行反流水红利
@asyncio.coroutine
def calcDayWater():
    #todo 同步中午12点前24小时的平博投注单
    try:
        betList=yield from get_wagers()
        for x in betList:
            yield from todo_pingbo_wagers(x)
    except Exception as e:
        logging.exception(e)
        logging.error('{}，中午流水计算平博注单修复失败,请及时人工修复平博注单,计算流水'.format(timestamp2Str(getNow())))
    else:
        strLastCheckTime = yield from classDataBaseMgr.getInstance().getCalcDayWaterTime()
        if strLastCheckTime is None:
            yield from classDataBaseMgr.getInstance().setCalcDayWaterTime(timeHelp.getNow())

        iLastCheckTime = int(strLastCheckTime)

        if not timeHelp.isSameBetDay(iLastCheckTime,timeHelp.getNow()):
            #隔bet日了,中午进行计算日流水，做返利活动
            #计算日流水
            yield from classDataBaseMgr.getInstance().setCalcDayWaterTime(timeHelp.getNow())
            iTodayStartTs = timeHelp.todayStartTimestamp()

            #获取昨日投注流水
            funFuture = asyncio.ensure_future(runExecuteAll(iTodayStartTs,iTodayStartTs-86400))
            listAllRet = yield from asyncio.wait_for(funFuture,10)

            #TODO log
            for var_ret in listAllRet:
                strAccountId = var_ret["loginId"]
                iValidCoin = int(var_ret["validWaterCoin"] * 100) #单位换算成分
                #拿用户数据
                if len(strAccountId) <= 0 or strAccountId is None:
                    logging.error("account data not find")
                    continue

                if iValidCoin <= 0:
                    logging.error("account [{}] validCoin [{}] not find".format(strAccountId,iValidCoin))
                    continue

                objPlayerData, objPlayLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
                if objPlayerData is None:
                    logging.error("account [{}] data not find")
                    continue

                dictVipCfg = vip_config.get(objPlayerData.iLevel,None)
                if dictVipCfg is None:
                    logging.error("accountId[{}] vipLevel[{}] cfg is not valid".format(objPlayerData.strAccountId,objPlayerData.iLevel))
                    continue
                    yield from classDataBaseMgr.getInstance().releasePlayerDataLock(objPlayerData.strAccountId)

                iRebate = int(iValidCoin / 1000 * dictVipCfg[rebate])
                balance = objPlayerData.iCoin + iRebate
                objPlayerData.iCoin += iRebate
                #TODO 日红利计算的bill要记录一下

                yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData,objPlayLock)

                yield from addPlayerBill(strAccountId, iValidCoin, balance, CoinOp.coinOpPingboDayWaterRebate, iValidWater=iRebate, strDes="日有效流水[{}]返利[{}]".format(iValidCoin/100,iRebate/100))

#每个月调用一次vip计算
@asyncio.coroutine
def calcMonthVip():
    strLastCheckTime = yield from classDataBaseMgr.getInstance().getCalcDayWaterTime()
    if strLastCheckTime is None:
        yield from classDataBaseMgr.getInstance().setCalcMonthWaterTime(timeHelp.getNow())

    iLastCheckTime = int(strLastCheckTime)

    if not timeHelp.isSameMonth(iLastCheckTime, timeHelp.getNow()):
        # 计算月流水
        yield from classDataBaseMgr.getInstance().setCalcMonthWaterTime(timeHelp.getNow())
        iLastStartTs = timeHelp.lastMonthStartTimestamp()
        iNowStartTs = timeHelp.monthStartTimestamp()

        funFuture = asyncio.ensure_future(runExecuteAll(iLastStartTs, iNowStartTs))
        listAllRet = asyncio.wait_for(funFuture,10)

        for var_ret in listAllRet:
            strAccountId = var_ret["loginId"]
            iValidCoin = var_ret["validWaterCoin"] * 100 #单位换算成分
            #拿用户数据
            if len(strAccountId) <= 0 or strAccountId is None:
                logging.error("account data not find")
                continue

            if int(iValidCoin) <= 0:
                logging.error("account [{}] validCoin [{}] not find".format(strAccountId,iValidCoin))
                continue

            objPlayerData, objPlayLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
            if objPlayerData is None:
                logging.error("account [{}] data not find")
                continue

            dictVipCfg = vip_config.get(objPlayerData.iLevel,None)
            if dictVipCfg is None:
                logging.error("accountId[{}] vipLevel[{}] cfg is not valid".format(objPlayerData.strAccountId,objPlayerData.iLevel))
                continue
                yield from classDataBaseMgr.getInstance().releasePlayerDataLock(objPlayerData.strAccountId)

            iVipLimit = dictVipCfg["keepValidWater"]
            if iValidCoin < iVipLimit:
                #降级
                if objPlayerData.iVip > 0:
                    objPlayerData.iVip -= 1
                    #TODO 自动发公告内容
                    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayLock)
                else:
                    #TODO bill
                    pass
            else:
                #TODO bill
                pass


""""
#实时计算用户的vip等级，如果用户产生有效流水，就去统计，去计算
@asyncio.coroutine
def calcTimingVip():

    listAccountIds = yield from classDataBaseMgr.getInstance().getCalcWaterPinboAccountId()

    for strAccountId in listAccountIds:
        iLastStartTs = timeHelp.lastMonthStartTimestamp()
        iNowStartTs = timeHelp.getNow()

        funFuture = asyncio.ensure_future(runExcuteOne(strAccountId,iLastStartTs, iNowStartTs))
        iValidCoin = asyncio.wait_for(funFuture)


        if int(iValidCoin) <= 0:
            logging.error("account [{}] validCoin [{}] not find".format(strAccountId, iValidCoin))
            continue

        objPlayerData, objPlayLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
        if objPlayerData is None:
            logging.error("account [{}] data not find")
            continue

        dictVipCfg = vip_config.get(objPlayerData.iLevel, None)
        if dictVipCfg is None:
            logging.error(
                "accountId[{}] vipLevel[{}] cfg is not valid".format(objPlayerData.strAccountId, objPlayerData.iLevel))
            continue
            yield from classDataBaseMgr.getInstance().releasePlayerDataLock(objPlayerData.strAccountId)

        #levelCalc.calPlayerVipLevel(objPlayerData.iLevel,objPlayerData.iLevelValidWater,)
"""

# 每月调用一次佣金计算
@asyncio.coroutine
def calcMonthCommission():
    strLastCheckTime = yield from classDataBaseMgr.getInstance().getCalcMonthCommissionTime()
    if strLastCheckTime is None:
        yield from classDataBaseMgr.getInstance().setCalcMonthCommissionTime(timeHelp.getNow())

    iLastCheckTime = int(strLastCheckTime)

    if not timeHelp.isSameMonth(iLastCheckTime, timeHelp.getNow()):
        # 计算月佣金
        yield from classDataBaseMgr.getInstance().setCalcMonthCommissionTime(timeHelp.getNow())
        startTime = timeHelp.lastMonthStartTimestamp()
        endTime = timeHelp.monthStartTimestamp()
        year = timeHelp.getYear(startTime)
        month = timeHelp.getMonth(startTime)
        if month <= 1:
            preYear = year - 1
            preMonth = 12
        else:
            preYear = year
            preMonth = month - 1
        agentConfig = yield from getAgentConfig()
        probetRate = agentConfig['电竞竞猜']
        pingboRate = agentConfig['平博体育']
        try:
            sql = "select agentId from dj_agent"
            result = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
            if result.rowcount <= 0:
                logging.info(repr("无代理用户"))
            else:
                for var in result:
                    agentId = var.agentId
                    with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
                        sql = "select balance from dj_agent_commission where agentId=%s and dateYear=%s and dateMonth=%s"
                        result = yield from conn.execute(sql, [agentId, preYear, preMonth])
                        if result.rowcount <= 0:
                            preBalance = 0
                        else:
                            for var_row in result:
                                preBalance = var_row.balance
                    newAccountNum = yield from classSqlBaseMgr.getInstance().getNewAccountCount(agentId, startTime,endTime)
                    activelyAccountNum = yield from classSqlBaseMgr.getInstance().getActivelyAccount(agentId, startTime,endTime)
                    pinboAllWinLoss = yield from classSqlBaseMgr.getInstance().getAccountPingboAllWinLoss(agentId,startTime,endTime)
                    probetAllWinLoss = yield from classSqlBaseMgr.getInstance().getAccountProbetAllWinCoin(agentId,startTime,endTime)
                    probetWinLoss = round(probetAllWinLoss)
                    pinboWinLoss = round(pinboAllWinLoss * 100)
                    # 平台费
                    if pinboWinLoss >= 0:
                        pingboPlatformCost = 0
                    else:
                        pingboPlatformCost = round(-pinboWinLoss * agentConfig['平博体育'])
                    if probetWinLoss >= 0:
                        probetPlatformCost = 0
                    else:
                        probetPlatformCost = round(-probetWinLoss * agentConfig['电竞竞猜'])
                    # 总输赢
                    winLoss = pinboWinLoss + probetWinLoss
                    # 平台费
                    platformCost = pingboPlatformCost + probetPlatformCost
                    pingboBackWater = yield from classSqlBaseMgr.getInstance().getAccountPinboBackWater(agentId,startTime,endTime)
                    probetBackWater = yield from classSqlBaseMgr.getInstance().getAccountProbetBackWater(agentId,startTime,endTime)
                    activetyBonus = yield from classSqlBaseMgr.getInstance().getAccountActivetyBonus(agentId, startTime,endTime)

                    pinboAllWater = yield from classSqlBaseMgr.getInstance().getAccountPingboWater(agentId, startTime,endTime)
                    probetAllWater = yield from classSqlBaseMgr.getInstance().getAccountProbetWater(agentId, startTime,endTime)
                    pingboWater = round(pinboAllWater * 100)
                    probetWater = round(probetAllWater)
                    allWater = pingboWater + probetWater
                    # 反水
                    backWater = round(pingboBackWater + probetBackWater)
                    activetyBonus = round(activetyBonus)
                    # 存提手续费
                    depositDrawingPoundage = yield from getDepositDrawingPoundage(agentId, startTime, endTime)

                    # 净利润，净输赢
                    netProfit = winLoss + platformCost + depositDrawingPoundage + activetyBonus + backWater
                    # 月结余
                    iBalance = netProfit + preBalance
                    if netProfit <= 0:
                        netProfit = -netProfit
                        for var_value in commission_config.values():
                            if var_value['leastNetWin'] <= netProfit <= var_value['mostNetWin']:
                                level = var_value['level']
                                proportion = agentConfig[level]
                    else:
                        netProfit = -netProfit
                        proportion = agentConfig['一档']

                    if iBalance < 0:
                        commission = round(-iBalance * proportion)
                        iBalance = 0
                    else:
                        commission = 0

                    sql = "select billId from dj_agent_commission where dateYear={} and dateMonth={} and agentId='{}'".format(
                        year, month, agentId)
                    result = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
                    if result.rowcount <= 0:
                        billId = str(uuid.uuid1())
                        if commission <= 0:
                            status = 2
                        else:
                            status = 1
                        objAgentCommissionData = yield from addCommissionBill(billId, agentId, year, month,
                                                                      newAccountNum,
                                                                      activelyAccountNum, probetWinLoss,
                                                                      pinboWinLoss, winLoss,probetRate,pingboRate,
                                                                      probetPlatformCost, pingboPlatformCost,
                                                                      platformCost, depositDrawingPoundage,
                                                                      backWater,activetyBonus, allWater,
                                                                      netProfit,preBalance,iBalance, proportion, commission, status)

                        yield from classDataBaseMgr.getInstance().addAgentCommissionData(objAgentCommissionData)
                    else:
                        for var in result:
                            billId = var.billId
                        if commission <= 0:
                            status = 2
                        else:
                            status = 1
                        objAgentCommissionData = yield from addCommissionBill(billId, agentId, year, month,
                                                                      newAccountNum,
                                                                      activelyAccountNum, probetWinLoss,
                                                                      pinboWinLoss, winLoss,probetRate,pingboRate,
                                                                      probetPlatformCost, pingboPlatformCost,
                                                                      platformCost, depositDrawingPoundage,
                                                                      backWater,activetyBonus, allWater,
                                                                      netProfit,preBalance,iBalance, proportion, commission, status)

                        yield from classDataBaseMgr.getInstance().addAgentCommissionData(objAgentCommissionData, billId)
        except Exception as e:
            #logging.exception(e)
            logging.exception(e)
            raise e


"""
# 每天调用一次，计算月初到现在的佣金，完成排行
@asyncio.coroutine
def calcMonthForNowCommission():
    strLastCheckTime = yield from classDataBaseMgr.getInstance().getCalcMonthByDayCommissionTime()
    if strLastCheckTime is None:
        yield from classDataBaseMgr.getInstance().setCalcMonthByDayCommissionTime(timeHelp.getNow())

    iLastCheckTime = int(strLastCheckTime)

    if not timeHelp.isSameDay(iLastCheckTime, timeHelp.getNow()):
        # 计算月初到现在的佣金
        yield from classDataBaseMgr.getInstance().setCalcMonthByDayCommissionTime(timeHelp.getNow())
        startTime = timeHelp.monthStartTimestamp()
        endTime = timeHelp.getNow()
        year = timeHelp.getYear(startTime)
        month = timeHelp.getMonth(startTime)

        if month <= 1:
            preYear = year - 1
            preMonth = 12
        else:
            preYear = year
            preMonth = month - 1

        agentConfig = yield from getAgentConfig()
        probetRate = agentConfig['电竞竞猜']
        pingboRate = agentConfig['平博体育']
        try:
            with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
                sql = "select balance from dj_agent_commission where agentId=%s and dateYear=%s and dateMonth=%s"
                result = yield from conn.execute(sql, [agentId, preYear, preMonth])
                if result.rowcount <= 0:
                    preBalance = 0
                else:
                    for var_row in result:
                        preBalance = var_row.balance
    
            newAccountNum = yield from classSqlBaseMgr.getInstance().getNewAccountCount(agentId, startTime, endTime)
            activelyAccountNum = yield from classSqlBaseMgr.getInstance().getActivelyAccount(agentId, startTime, endTime)
            pinboAllWinLoss = yield from classSqlBaseMgr.getInstance().getAccountPingboAllWinLoss(agentId, startTime, endTime)
            probetAllWinLoss = yield from classSqlBaseMgr.getInstance().getAccountProbetAllWinCoin(agentId, startTime, endTime)
            probetWinLoss = round(probetAllWinLoss)
            pinboWinLoss = round(pinboAllWinLoss * 100)
            # 平台费
            if pinboWinLoss >= 0:
                pingboPlatformCost = 0
            else:
                pingboPlatformCost = round(-pinboWinLoss * agentConfig['平博体育'])
            if probetWinLoss >= 0:
                probetPlatformCost = 0
            else:
                probetPlatformCost = round(-probetWinLoss * agentConfig['电竞竞猜'])
            pingboBackWater = yield from classSqlBaseMgr.getInstance().getAccountPinboBackWater(agentId, startTime, endTime)
            probetBackWater = yield from classSqlBaseMgr.getInstance().getAccountProbetBackWater(agentId, startTime, endTime)
            # 活动返奖
            activetyBonus = yield from classSqlBaseMgr.getInstance().getAccountActivetyBonus(agentId, startTime,endTime)
    
            pinboAllWater = yield from classSqlBaseMgr.getInstance().getAccountPingboWater(agentId, startTime, endTime)
            probetAllWater = yield from classSqlBaseMgr.getInstance().getAccountProbetWater(agentId, startTime, endTime)
            pingboWater = round(pinboAllWater*100)
            probetWater = round(probetAllWater)
            allWater = pingboWater+probetWater
    
            # 反水
            backWater = round(pingboBackWater + probetBackWater)
            # 返奖
            activetyBonus = round(activetyBonus)
            # 存提手续费
            depositDrawingPoundage = yield from getDepositDrawingPoundage(agentId, startTime, endTime)
    
            #净利润，净输赢
            netProfit = probetWinLoss+pingboPlatformCost+pinboWinLoss+probetPlatformCost+depositDrawingPoundage+activetyBonus+backWater
            # 月结余
            iBalance = netProfit + preBalance
            if netProfit <= 0:
                netProfit = -netProfit
                for var_value in commission_config.values():
                    if var_value['leastNetWin'] <= netProfit <= var_value['mostNetWin']:
                        level = var_value['level']
                        proportion = agentConfig[level]
            else:
                netProfit = -netProfit
                proportion = agentConfig['一档']
    
            # 总输赢
            winLoss = pinboWinLoss + probetWinLoss
            # 平台费
            platformCost = pingboPlatformCost + probetPlatformCost
    
            if iBalance < 0:
                commission = round(-iBalance * proportion)
                iBalance = 0
            else:
                commission = 0
    
            sql = "select billId from dj_agent_commission where dateYear={} and dateMonth={} and agentId='{}'".format(
                year, month, agentId)
            result = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
            if result.rowcount <= 0:
                billId = str(uuid.uuid1())
                if commission <= 0:
                    status = 2
                else:
                    status = 1
                objAgentCommissionData = yield from addCommissionBill(billId, agentId, year, month,
                                                                          newAccountNum,
                                                                          activelyAccountNum, probetWinLoss,
                                                                          pinboWinLoss, winLoss,probetRate,pingboRate,
                                                                          probetPlatformCost, pingboPlatformCost,
                                                                          platformCost, depositDrawingPoundage,
                                                                          backWater,activetyBonus, allWater,
                                                                          netProfit,preBalance,iBalance, proportion, commission, status)
    
                yield from classDataBaseMgr.getInstance().addAgentCommissionData(objAgentCommissionData)
            else:
                for var in result:
                    billId = var.billId
                if commission <= 0:
                    status = 2
                else:
                    status = 1
                objAgentCommissionData = yield from addCommissionBill(billId, agentId, year, month,
                                                                          newAccountNum,
                                                                          activelyAccountNum, probetWinLoss,
                                                                          pinboWinLoss, winLoss,probetRate,pingboRate,
                                                                          probetPlatformCost, pingboPlatformCost,
                                                                          platformCost, depositDrawingPoundage,
                                                                          backWater,activetyBonus, allWater,
                                                                          netProfit,preBalance,iBalance, proportion, commission, status)
    
                yield from classDataBaseMgr.getInstance().addAgentCommissionData(objAgentCommissionData, billId)
        except Exception as e:
            logging.exception(e)
            raise e
"""