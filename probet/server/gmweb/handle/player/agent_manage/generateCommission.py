import asyncio
from lib.jsonhelp import classJsonDump
import logging
import uuid
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required, permission_required
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.timehelp import timeHelp
from datetime import datetime
from config.commissionConfig import commission_config
from datawrapper.agentDataOpWrapper import addCommissionBill,getDepositDrawingPoundage,getAgentConfig



class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


# 每月调一次
@token_required
@permission_required('代理概况')
@asyncio.coroutine
def handleHttp(request:dict):
    """生成佣金报表单"""

    agentId=request.get('agentId','')
    year = request.get('year',0)
    month = request.get('month', 0)

    if not all([year,month]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    begin = datetime(year,month,1)
    if month == 12:
        end = datetime(year+1,1,1)
    else:
        end = datetime(year,month+1,1)
    startTime = timeHelp.date2timestamp(begin)
    endTime = timeHelp.date2timestamp(end)

    if month <= 1:
        preYear = year - 1
        preMonth = 12
    else:
        preYear = year
        preMonth = month - 1

    agentConfig = yield from getAgentConfig()
    probetRate = agentConfig['电竞竞猜']
    pingboRate = agentConfig['平博体育']
    if agentId:
        try:
            with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
                sql = "select balance from dj_agent_commission where agentId=%s and dateYear=%s and dateMonth=%s"
                result = yield from conn.execute(sql, [agentId,preYear,preMonth])
                if result.rowcount <= 0:
                    preBalance = 0
                else:
                    for var_row in result:
                        preBalance = var_row.balance
        except Exception as e:
            logging.error(repr(e))
            raise e
        objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(agentId)
        if objPlayerData is None:
            raise exceptionLogic(errorLogic.agent_data_not_found)
        if objPlayerData.iUserType != 2:
            raise exceptionLogic(errorLogic.agent_data_not_found)
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
        # 总输赢
        winLoss = pinboWinLoss + probetWinLoss
        # 平台费
        platformCost = pingboPlatformCost + probetPlatformCost
        pingboBackWater = yield from classSqlBaseMgr.getInstance().getAccountPinboBackWater(agentId, startTime, endTime)
        probetBackWater = yield from classSqlBaseMgr.getInstance().getAccountProbetBackWater(agentId, startTime, endTime)
        activetyBonus = yield from classSqlBaseMgr.getInstance().getAccountActivetyBonus(agentId, startTime, endTime)
        # 流水
        pinboAllWater = yield from classSqlBaseMgr.getInstance().getAccountPingboWater(agentId, startTime, endTime)
        probetAllWater = yield from classSqlBaseMgr.getInstance().getAccountProbetWater(agentId, startTime, endTime)
        pingboWater = round(pinboAllWater*100)
        probetWater = round(probetAllWater)
        allWater = pingboWater+probetWater

        # 反水
        backWater = round(pingboBackWater + probetBackWater)
        activetyBonus = round(activetyBonus)
        # 存提手续费
        depositDrawingPoundage = yield from getDepositDrawingPoundage(agentId, startTime, endTime)

        # 净利润，净输赢
        netProfit = winLoss + platformCost + depositDrawingPoundage + activetyBonus + backWater
        # 月结余
        iBalance = netProfit + preBalance
        if netProfit<=0:
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
            if commission <=0:
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
            if commission <=0:
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
        objRsp = cResp()
        return classJsonDump.dumps(objRsp)
    else:
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
            objRsp = cResp()
            return classJsonDump.dumps(objRsp)
        except Exception as e:
            logging.exception(e)
            raise e


