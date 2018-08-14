import asyncio
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.tool import agent_token_required
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from lib.timehelp import timeHelp
from datawrapper.agentDataOpWrapper import getAgentConfig


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@agent_token_required
@asyncio.coroutine
def handleHttp(request: dict):
    """财务报表-存提手续费"""
    objRep = cResp()

    agentId = request.get('agentId', '')
    startTime = request.get('startTime', 0)
    endTime = request.get('endTime', 0)

    if not all([startTime, endTime]):
        startTime = timeHelp.monthStartTimestamp()
        endTime = timeHelp.getNow()
    agentConfig = yield from getAgentConfig()

    BankTransferDeposit = yield from classSqlBaseMgr.getInstance().getBankTransfer(agentId, startTime, endTime)
    UnionpayDeposit = yield from classSqlBaseMgr.getInstance().getUnionpay(agentId, startTime, endTime)
    QQpayDeposit = yield from classSqlBaseMgr.getInstance().getQQpay(agentId, startTime, endTime)
    AlipayDeposit = yield from classSqlBaseMgr.getInstance().getAlipay(agentId, startTime, endTime)
    AlipayTransferDeposit = yield from classSqlBaseMgr.getInstance().getAlipayTransfer(agentId, startTime, endTime)
    # WeixinDeposit = yield from classSqlBaseMgr.getInstance().getWeixinPay(agentId, startTime, endTime)
    WeixinTransferDeposit = yield from classSqlBaseMgr.getInstance().getWeixinTransfer(agentId, startTime, endTime)
    drawingNum = yield from classSqlBaseMgr.getInstance().getAccountAllDrawing(agentId, startTime, endTime)
    BankTransfer = {}
    Unionpay = {}
    QQpay = {}
    Alipay = {}
    AlipayTransfer = {}
    Weixinpay = {}
    WeixinTransfer = {}
    drawing = {}

    drawingAllNum = '%.2f' % round(drawingNum / 100, 2)
    BankTransferAllDeposit = '%.2f' % round(BankTransferDeposit / 100, 2)
    UnionpayAllDeposit = '%.2f' % round(UnionpayDeposit / 100, 2)
    QQpayAllDeposit = '%.2f' % round(QQpayDeposit / 100, 2)
    AlipayAllDeposit = '%.2f' % round(AlipayDeposit / 100, 2)
    AlipayTransferAllDeposit = '%.2f' % round(AlipayTransferDeposit / 100, 2)
    # WeixinAllDeposit = '%.2f' % round(WeixinDeposit / 100, 2)
    WeixinTransferAllDeposit = '%.2f' % round(WeixinTransferDeposit / 100, 2)

    drawingPoundage = '%.2f' % (round(drawingNum) * agentConfig['提款']/ 100)
    BankTransferPoundage = '%.2f' % (round(BankTransferDeposit) * agentConfig['银行卡转账']/ 100)
    UnionpayPoundage = '%.2f' % (round(UnionpayDeposit) * agentConfig['银联扫码']/100)
    QQpayPoundage = '%.2f' % (round(QQpayDeposit) * agentConfig['QQ扫码']/100)
    AlipayPoundage = '%.2f' % (round(AlipayDeposit) * agentConfig['支付宝扫码']/100)
    AlipayTransferPoundage = '%.2f' % (round(AlipayTransferDeposit) * agentConfig['支付宝转账']/ 100)
    # WeixinPoundage = '%.2f' % (round(WeixinDeposit) * agentConfig['微信扫码']/ 100)
    WeixinTransferPoundage = '%.2f' % (round(WeixinTransferDeposit) * agentConfig['微信转账']/ 100)

    drawing['type'] = '提款'
    drawing['coin'] = drawingAllNum
    drawing['rate'] = '{}%'.format(agentConfig['提款']*100)
    drawing['poundage'] = drawingPoundage

    BankTransfer['type'] = '银行卡转账'
    BankTransfer['coin'] = BankTransferAllDeposit
    BankTransfer['rate'] = '{}%'.format(agentConfig['银行卡转账']*100)
    BankTransfer['poundage'] = BankTransferPoundage

    Unionpay['type'] = '银联扫码'
    Unionpay['coin'] = UnionpayAllDeposit
    Unionpay['rate'] = '{}%'.format(agentConfig['银联扫码']*100)
    Unionpay['poundage'] = QQpayPoundage

    QQpay['type'] = 'qq支付'
    QQpay['coin'] = QQpayAllDeposit
    QQpay['rate'] = '{}%'.format(agentConfig['QQ扫码']*100)
    QQpay['poundage'] = UnionpayPoundage

    Alipay['type'] = '支付宝扫码'
    Alipay['coin'] = AlipayAllDeposit
    Alipay['rate'] = '{}%'.format(agentConfig['支付宝扫码']*100)
    Alipay['poundage'] = AlipayPoundage

    AlipayTransfer['type'] = '支付宝转账'
    AlipayTransfer['coin'] = AlipayTransferAllDeposit
    AlipayTransfer['rate'] = '{}%'.format(agentConfig['支付宝转账']*100)
    AlipayTransfer['poundage'] = AlipayTransferPoundage

    # Weixinpay['type'] = '微信扫码'
    # Weixinpay['coin'] = WeixinAllDeposit
    # Weixinpay['rate'] = '{}%'.format(agentConfig['微信扫码'] * 100)
    # Weixinpay['poundage'] = WeixinPoundage

    WeixinTransfer['type'] = '微信转账'
    WeixinTransfer['coin'] = WeixinTransferAllDeposit
    WeixinTransfer['rate'] = '{}%'.format(agentConfig['微信转账']*100)
    WeixinTransfer['poundage'] = WeixinTransferPoundage

    objRep.data.append(BankTransfer)
    objRep.data.append(Unionpay)
    objRep.data.append(QQpay)
    objRep.data.append(Alipay)
    objRep.data.append(AlipayTransfer)
    # objRep.data.append(Weixinpay)
    objRep.data.append(WeixinTransfer)
    objRep.data.append(drawing)
    return classJsonDump.dumps(objRep)
