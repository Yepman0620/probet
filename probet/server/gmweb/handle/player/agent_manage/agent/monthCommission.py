
import asyncio
from lib.jsonhelp import classJsonDump
import logging
import uuid
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import errorLogic, exceptionLogic
from lib.tool import agent_token_required
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


@agent_token_required
@asyncio.coroutine
def handleHttp(request:dict):
    """每月实时佣金账单"""
    objRsp = cResp()

    agentId = request.get('agentId','')

    year = datetime.now().year
    month = datetime.now().month

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
            objAgentCommissionData = yield from addCommissionBill(billId, agentId, year, month,
                                                                      newAccountNum,
                                                                      activelyAccountNum, probetWinLoss,
                                                                      pinboWinLoss, winLoss,probetRate,pingboRate,
                                                                      probetPlatformCost, pingboPlatformCost,
                                                                      platformCost, depositDrawingPoundage,
                                                                      backWater,activetyBonus, allWater,
                                                                      netProfit,preBalance,iBalance, proportion, commission, 3)

            yield from classDataBaseMgr.getInstance().addAgentCommissionData(objAgentCommissionData)
        else:
            for var in result:
                billId = var.billId
            objAgentCommissionData = yield from addCommissionBill(billId, agentId, year, month,
                                                                      newAccountNum,
                                                                      activelyAccountNum, probetWinLoss,
                                                                      pinboWinLoss, winLoss,probetRate,pingboRate,
                                                                      probetPlatformCost, pingboPlatformCost,
                                                                      platformCost, depositDrawingPoundage,
                                                                      backWater,activetyBonus, allWater,
                                                                      netProfit,preBalance,iBalance, proportion, commission, 3)

            yield from classDataBaseMgr.getInstance().addAgentCommissionData(objAgentCommissionData, billId)
        yield from asyncio.sleep(1)
        sql = "select * from dj_agent_commission where agentId=%s and dateYear=%s and dateMonth=%s "
        params = [agentId, year, month]
        with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
            result = yield from conn.execute(sql, params)
            if result.rowcount<=0:
                return classJsonDump.dumps(objRsp)
            else:
                for var_row in result:
                    commissionDict = {}
                    commissionDict['date'] = str(var_row.dateYear) + '/' + str(var_row.dateMonth)
                    commissionDict['activelyAccountNum'] = var_row.activeAccount
                    commissionDict['winLoss'] = '%.2f' % round(-var_row.winLoss / 100, 2)
                    commissionDict['dividend'] = '%.2f' % round((var_row.backWater+var_row.bonus) / 100, 2)
                    commissionDict['pingboWinLoss'] = '%.2f' % round(var_row.pingboWinLoss / 100, 2)
                    commissionDict['probetWinLoss'] = '%.2f' % round(var_row.probetWinLoss / 100, 2)
                    commissionDict['pingboCost'] = '%.2f' % round(var_row.pingboCost / 100, 2)
                    commissionDict['probetCost'] = '%.2f' % round(var_row.probetCost / 100, 2)
                    commissionDict['pingboRate'] = '{}%'.format(var_row.probetRate * 100)
                    commissionDict['probetRate'] = '{}%'.format(var_row.pingboRate * 100)
                    commissionDict['depositDrawingCost'] = '%.2f' % round(var_row.depositDrawingCost / 100, 2)
                    commissionDict['backWater'] = '%.2f' % round(var_row.backWater / 100, 2)
                    commissionDict['bonus'] = '%.2f' % round(var_row.bonus / 100, 2)
                    commissionDict['netProfit'] = '%.2f' % round(var_row.netProfit / 100, 2)
                    commissionDict['balance'] = '%.2f' % round(-(var_row.preBalance / 100), 2)
                    commissionDict['commissionRate'] = '{}%'.format(var_row.commissionRate * 100)
                    commissionDict['commission'] = '%.2f' % round(var_row.commission / 100, 2)
                    commissionDict['status'] = var_row.status
                    objRsp.data.append(commissionDict)
        return classJsonDump.dumps(objRsp)
    except Exception as e:
        logging.exception(e)
        raise e

