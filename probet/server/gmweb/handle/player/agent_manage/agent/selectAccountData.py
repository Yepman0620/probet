import asyncio
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.tool import agent_token_required
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from lib.timehelp import timeHelp


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@agent_token_required
@asyncio.coroutine
def handleHttp(request: dict):
    """用户信息"""
    objRep = cResp()

    agentId = request.get('agentId', '')
    accountId = request.get('accountId', '')
    startTime = request.get('startTime', 0)
    endTime = request.get('endTime', 0)
    pn = request.get('pn', 1)

    if not pn:
        raise exceptionLogic(errorLogic.client_param_invalid)

    if not all([startTime, endTime]):
        startTime = timeHelp.monthStartTimestamp()
        endTime = timeHelp.getNow()
    if accountId:
        sql_count = "select count(accountId) from dj_account where agentId=%s and accountId=%s and loginTime between %s and %s"
        sql = "select accountId,regTime,loginTime from dj_account where agentId=%s and accountId=%s and loginTime between %s and %s "
        sql_count_params=[agentId,accountId,startTime,endTime]
        sql_params=[agentId,accountId,startTime,endTime]
    else:
        sql_count = "select count(accountId) from dj_account where agentId=%s and loginTime between %s and %s "
        sql = "select accountId,regTime,loginTime from dj_account where agentId=%s and loginTime between %s and %s order by loginTime desc limit %s offset %s"
        sql_count_params = [agentId,startTime,endTime]
        sql_params = [agentId,startTime,endTime, 10, (pn - 1) * 10]
    try:
        with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
            ret = yield from conn.execute(sql_count,sql_count_params)
            result = yield from conn.execute(sql,sql_params)
            if ret.rowcount <= 0:
                return classJsonDump.dumps(objRep)
            else:
                for var in ret:
                    count = var[0]
                accountDataList = []
                for var_row in result:
                    accountDataDict = {}
                    accountId = var_row.accountId
                    regTime = var_row.regTime
                    loginTime = var_row.loginTime
                    balance = yield from classSqlBaseMgr.getInstance().getAccountAllBalance(accountId)
                    deposit = yield from classSqlBaseMgr.getInstance().getAccountDeposit(accountId, startTime, endTime)
                    drawing = yield from classSqlBaseMgr.getInstance().getAccountDrawing(accountId, startTime, endTime)

                    pinboAllWinLoss = yield from classSqlBaseMgr.getInstance().getAccountPingboWinLoss(accountId, startTime,endTime)
                    probetAllWinLoss = yield from classSqlBaseMgr.getInstance().getAccountProbetWinCoin(accountId, startTime,endTime)
                    pingboWinLoss = round(pinboAllWinLoss*100)

                    accountDataDict['accountId'] = accountId
                    accountDataDict['regTime'] = regTime
                    accountDataDict['loginTime'] = loginTime
                    accountDataDict['balance'] = "%.2f"%round(balance/100, 2)
                    accountDataDict['deposit'] = "%.2f"%round(deposit/100, 2)
                    accountDataDict['drawing'] = "%.2f"%round(drawing/100, 2)
                    accountDataDict['lossWin'] = "%.2f"%round((pingboWinLoss + probetAllWinLoss)/100, 2)
                    accountDataList.append(accountDataDict)
            objRep.data = accountDataList
            objRep.count = count
            return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)
