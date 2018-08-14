import asyncio
import json
import logging
from logic.data.userData import classAgentCommissionData
from error.errorCode import errorLogic,exceptionLogic,exceptionLogic
from lib.timehelp import timeHelp
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr


def getAgentConfig():
    agentConfigs = yield from classDataBaseMgr.getInstance().getAgentConfig()
    agentConfig = {}
    for bytesAgent in agentConfigs:
        agentConfig[bytesAgent.strName]=bytesAgent.iRate/1000
    return agentConfig


@asyncio.coroutine
def addCommissionBill(billId,agentId,year,month,newAccountNum,activelyAccountNum,probetWinLoss,pinboWinLoss,winLoss,probetRate,pingboRate,probetPlatformCost,pingboPlatformCost,platformCost,depositDrawingPoundage,backWater,activetyBonus,allWater,netProfit,preBalance,balance,proportion,commission,status):
    """生成佣金报表"""
    objAgentCommissionData = classAgentCommissionData()
    objAgentCommissionData.strBillId = billId
    objAgentCommissionData.strAgentId = agentId
    objAgentCommissionData.iTime = timeHelp.getNow()
    objAgentCommissionData.iYear = year
    objAgentCommissionData.iMonth = month
    objAgentCommissionData.iNewAccount = newAccountNum
    objAgentCommissionData.iActiveAccount = activelyAccountNum
    objAgentCommissionData.iProbetWinLoss = -probetWinLoss
    objAgentCommissionData.iPingboWinLoss = -pinboWinLoss
    objAgentCommissionData.iWinLoss = winLoss
    objAgentCommissionData.fProbetRate = probetRate
    objAgentCommissionData.fPingboRate = pingboRate
    objAgentCommissionData.iProbetCost = probetPlatformCost
    objAgentCommissionData.iPingboCost = pingboPlatformCost
    objAgentCommissionData.iPlatformCost = platformCost
    objAgentCommissionData.iDepositDrawingCost = depositDrawingPoundage
    objAgentCommissionData.iBackWater = backWater
    objAgentCommissionData.iBonus = activetyBonus
    objAgentCommissionData.iWater = allWater
    objAgentCommissionData.iNetProfit = netProfit
    objAgentCommissionData.iPreBalance = preBalance
    objAgentCommissionData.iBalance = balance
    objAgentCommissionData.fCommissionRate = proportion
    objAgentCommissionData.iCommission = commission
    objAgentCommissionData.iStatus = status

    return objAgentCommissionData


def getDepositDrawingPoundage(agentId, startTime, endTime):
    """下线用户总存提手续费"""
    agentConfig = yield from getAgentConfig()
    # 存提
    BankTransferDeposit = yield from classSqlBaseMgr.getInstance().getBankTransfer(agentId, startTime, endTime)
    UnionpayDeposit = yield from classSqlBaseMgr.getInstance().getUnionpay(agentId, startTime, endTime)
    QQpayDeposit = yield from classSqlBaseMgr.getInstance().getQQpay(agentId, startTime, endTime)
    AlipayDeposit = yield from classSqlBaseMgr.getInstance().getAlipay(agentId, startTime, endTime)
    AlipayTransferDeposit = yield from classSqlBaseMgr.getInstance().getAlipayTransfer(agentId, startTime, endTime)
    WeixinTransferDeposit = yield from classSqlBaseMgr.getInstance().getWeixinTransfer(agentId, startTime, endTime)
    drawingNum = yield from classSqlBaseMgr.getInstance().getAccountAllDrawing(agentId, startTime, endTime)

    drawingPoundage = round(drawingNum) * agentConfig['提款']
    BankTransferPoundage = round(BankTransferDeposit) * agentConfig['银行卡转账']
    UnionpayPoundage = round(UnionpayDeposit) * agentConfig['银联扫码']
    QQpayPoundage = round(QQpayDeposit) * agentConfig['QQ扫码']
    AlipayPoundage = round(AlipayDeposit) * agentConfig['支付宝扫码']
    AlipayTransferPoundage = round(AlipayTransferDeposit) * agentConfig['支付宝转账']
    WeixinTransferPoundage = round(WeixinTransferDeposit) * agentConfig['微信转账']
    # 存提手续费
    depositDrawingPoundage = round(drawingPoundage + BankTransferPoundage + UnionpayPoundage + QQpayPoundage + AlipayPoundage + WeixinTransferPoundage + AlipayTransferPoundage)

    return depositDrawingPoundage


def getAccountDepositDrawingPoundage(accountId, startTime, endTime):
    """下线用户总存提手续费"""
    agentConfig = yield from getAgentConfig()
    # 存提
    BankTransferDeposit = yield from classSqlBaseMgr.getInstance().getAccountBankTransfer(accountId, startTime, endTime)
    UnionpayDeposit = yield from classSqlBaseMgr.getInstance().getAccountUnionpay(accountId, startTime, endTime)
    QQpayDeposit = yield from classSqlBaseMgr.getInstance().getAccountQQpay(accountId, startTime, endTime)
    AlipayDeposit = yield from classSqlBaseMgr.getInstance().getAccountAlipay(accountId, startTime, endTime)
    AlipayTransferDeposit = yield from classSqlBaseMgr.getInstance().getAccountAlipayTransfer(accountId, startTime, endTime)
    WeixinTransferDeposit = yield from classSqlBaseMgr.getInstance().getAccountWeixinTransfer(accountId, startTime, endTime)
    drawingNum = yield from classSqlBaseMgr.getInstance().getAccountDrawing(accountId, startTime, endTime)

    drawingPoundage = round(drawingNum) * agentConfig['提款']
    BankTransferPoundage = round(BankTransferDeposit) * agentConfig['银行卡转账']
    UnionpayPoundage = round(UnionpayDeposit) * agentConfig['银联扫码']
    QQpayPoundage = round(QQpayDeposit) * agentConfig['QQ扫码']
    AlipayPoundage = round(AlipayDeposit) * agentConfig['支付宝扫码']
    AlipayTransferPoundage = round(AlipayTransferDeposit) * agentConfig['支付宝转账']
    WeixinTransferPoundage = round(WeixinTransferDeposit) * agentConfig['微信转账']
    # 存提手续费
    depositDrawingPoundage = round(drawingPoundage + BankTransferPoundage + UnionpayPoundage + QQpayPoundage + AlipayPoundage + WeixinTransferPoundage + AlipayTransferPoundage)

    return depositDrawingPoundage




