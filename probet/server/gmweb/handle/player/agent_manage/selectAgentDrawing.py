import asyncio
import json
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from lib.timehelp import timeHelp
from datetime import datetime
import time


class cResp():
    def __init__(self):
        self.ret = 0
        self.count = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('代理提款查询')
@asyncio.coroutine
def handleHttp(request: dict):
    """代理提款查询"""
    objRep = cResp()

    agentId = request.get('agentId', '')
    year = request.get('year', 0)
    month = request.get('month', 0)
    pn = request.get('pn', 1)

    if not all([agentId, pn]):
        raise exceptionLogic(errorLogic.client_param_invalid)
    objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(agentId)
    if objPlayerData is None:
        raise exceptionLogic(errorLogic.player_data_not_found)
    if objPlayerData.iUserType != 2:
        raise exceptionLogic(errorLogic.agent_data_not_found)
    try:
        conn = classSqlBaseMgr.getInstance()
        if (not month) and (not year):
            sql_count = "select count(orderId) from dj_coin_history where accountId='{}' and tradeType=2".format(
                agentId)
            sql = "select orderTime,coinNum,tradeState,accountId,endTime,transTo from dj_coin_history where accountId='{}' and tradeType=2 order by orderTime desc limit {} offset {}".format(
                agentId, 10, (pn - 1) *  10)
        elif year and (not month):
            begin = datetime(year, 1, 1)
            stop = datetime(year+1, 1, 1)
            start_time = timeHelp.date2timestamp(begin)
            end_time = timeHelp.date2timestamp(stop)
            sql_count = "select count(orderId) from dj_coin_history where accountId='{}' and tradeType=2 and orderTime between {} and {}".format(
                agentId,start_time,end_time)
            sql = "select orderTime,coinNum,tradeState,accountId,endTime,transTo from dj_coin_history where accountId='{}' and tradeType=2 and orderTime between {} and {} order by orderTime desc limit {} offset {}".format(
                agentId,start_time,end_time,  10, (pn - 1) * 10)
        elif (not year) and month:
            year = datetime.now().year
            begin = datetime(year, month, 1)
            if month == 12:
                stop = datetime(year + 1, 1, 1)
            else:
                stop = datetime(year, month + 1, 1)
            start_time = timeHelp.date2timestamp(begin)
            end_time = timeHelp.date2timestamp(stop)
            sql_count = "select count(orderId) from dj_coin_history where accountId='{}' and tradeType=2 and orderTime between {} and {}".format(
                agentId, start_time, end_time)
            sql = "select orderTime,coinNum,tradeState,accountId,endTime,transTo from dj_coin_history where accountId='{}' and tradeType=2 and orderTime between {} and {} order by orderTime desc limit {} offset {}".format(
                agentId, start_time, end_time, 10, (pn - 1) *  10)
        else:
            begin = datetime(year, month, 1)
            if month == 12:
                stop = datetime(year + 1, 1, 1)
            else:
                stop = datetime(year, month + 1, 1)
            start_time = timeHelp.date2timestamp(begin)
            end_time = timeHelp.date2timestamp(stop)
            sql_count = "select count(orderId) from dj_coin_history where accountId='{}' and tradeType=2 and orderTime between {} and {} limit {} offset {}".format(
                agentId, start_time, end_time,  10, (pn - 1) * 10)
            sql = "select orderTime,coinNum,tradeState,accountId,endTime,transTo from dj_coin_history where accountId='{}' and tradeType=2 and orderTime between {} and {} limit {} offset {}".format(
                agentId, start_time, end_time,  10, (pn - 1) * 10)
        count_ret = yield from conn._exeCute(sql_count)
        listRet = yield from conn._exeCute(sql)
        datas = yield from listRet.fetchall()
        if count_ret.rowcount <= 0:
            return classJsonDump.dumps(objRep)
        else:
            for var in count_ret:
                count = var[0]
            dataList = []
            for x in datas:
                dataDict = {}
                dataDict['date'] = str(timeHelp.getYear(x.orderTime))+'/'+str(timeHelp.getMonth(x.orderTime))
                dataDict['orderTime'] = x.orderTime
                dataDict['coinNum'] = "%.2f" % round(x.coinNum / 100, 2)
                dataDict['tradeState'] = x.tradeState
                dataDict['accountId'] = x.accountId
                dataDict['endTime'] = x.endTime
                dataDict['transTo'] = x.transTo
                dataList.append(dataDict)
            objRep.count = count
            objRep.data = dataList
            if pn==1:
                fileName = __name__
                nameList = fileName.split('.')
                methodName = nameList.pop()
                # 日志
                dictActionBill = {
                    'billType': 'adminActionBill',
                    'accountId': request.get('accountId', ''),
                    'action': "查询代理提款信息",
                    'actionTime': timeHelp.getNow(),
                    'actionMethod': methodName,
                    'actionDetail': "查询代理:{}提款信息".format(agentId),
                    'actionIp': request.get('srcIp', ''),
                }
                logging.getLogger('bill').info(json.dumps(dictActionBill))
            return classJsonDump.dumps(objRep)
    except exceptionLogic as e:
        logging.exception(e)
        raise e
