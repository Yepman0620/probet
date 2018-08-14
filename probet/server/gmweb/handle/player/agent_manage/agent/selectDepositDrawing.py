import asyncio
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.tool import agent_token_required
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from lib.timehelp import timeHelp
from lib.constants import RATE_LIST
from datawrapper.agentDataOpWrapper import getDepositDrawingPoundage,getAgentConfig


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@agent_token_required
@asyncio.coroutine
def handleHttp(request: dict):
    """存提"""
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
    try:
        agentConfig = yield from getAgentConfig()
        with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
            if accountId:
                sql_count = "select count(orderId) from dj_coin_history where accountId=%s and (tradeType=1 or tradeType=2) and tradeState=1 and orderTime between %s and %s"
                sql = "select orderId,orderTime,coinNum,balance,tradeType,tradeState,transFrom,accountId from dj_coin_history where accountId=%s and (tradeType=1 or tradeType=2) and tradeState=1 and orderTime between %s and %s order by orderTime desc limit %s offset %s"
                sql_count_params=[accountId,startTime,endTime]
                sql_params=[accountId,startTime,endTime, 10, (pn - 1) * 10]
            else:
                userIds = yield from classSqlBaseMgr.getInstance().getAccountByAgent(agentId)
                if len(userIds)==0:
                    return classJsonDump.dumps(objRep)
                sql_count = "select count(orderId) from dj_coin_history where accountId in (%s) and (tradeType=1 or tradeType=2) and tradeState=1 "%",".join(["%s"]*len(userIds))
                sql_count=sql_count+" and orderTime between %s and %s"
                params=userIds+[startTime, endTime]
                sql_count_params = params
                sql = "select orderId,orderTime,coinNum,balance,tradeType,tradeState,transFrom,accountId from dj_coin_history where accountId in (%s) and (tradeType=1 or tradeType=2) and tradeState=1 "%",".join(["%s"]*len(userIds))
                sql=sql+" and orderTime between %s and %s order by orderTime desc limit %s offset %s"
                sql_params = params+[ 10, (pn - 1) * 10]
            ret = yield from conn.execute(sql_count,sql_count_params)
            result = yield from conn.execute(sql,sql_params)
            if ret.rowcount <= 0:
                return classJsonDump.dumps(objRep)
            else:
                for var in ret:
                    count = var[0]
                desipotDrawingList = []
                for var_row in result:
                    desipotDrawingDict = {}
                    rate = var_row.transFrom
                    desipotDrawingDict['orderId'] = var_row.orderId
                    desipotDrawingDict['orderTime'] = var_row.orderTime
                    desipotDrawingDict['coinNum'] = "%.2f"%round(var_row.coinNum/100,2)
                    desipotDrawingDict['tradeType'] = var_row.tradeType
                    desipotDrawingDict['accountId'] = var_row.accountId
                    desipotDrawingDict['balance'] = "%.2f"%round(var_row.balance/100,2)
                    if rate in RATE_LIST:
                        desipotDrawingDict['cost'] = "%.2f"%round((var_row.coinNum *agentConfig[rate])/100,2)
                        desipotDrawingDict['transFrom'] = var_row.transFrom
                    else:
                        desipotDrawingDict['cost'] = "%.2f" % round((var_row.coinNum * agentConfig['提款']) / 100, 2)
                        desipotDrawingDict['transFrom'] = '提款成功'
                    desipotDrawingList.append(desipotDrawingDict)
            objRep.data = desipotDrawingList
            objRep.count = count
            return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)
