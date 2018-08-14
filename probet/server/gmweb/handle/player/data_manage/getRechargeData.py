import asyncio
import json
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.tools import token_required, permission_required
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow
from logic.logicmgr.checkParamValid import checkIsInt

class cData():
    def __init__(self):
        self.payTime=0
        # self.regCount=0
        # self.retainRate=[]

class cResp():
    def __init__(self):
        self.ret = 0
        self.count = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('充值数据查询')
@asyncio.coroutine
def handleHttp(request: dict):
    """根据时间，渠道获取充值数据"""
    channel = request.get('channel', '')
    startTime = request.get('startTime', 0)
    endTime = request.get('endTime', 0)
    pn = request.get('pn', 1)
    objRep = cResp()

    if not all([startTime,endTime]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    if (not checkIsInt(startTime)) or (not checkIsInt(endTime)) or (not checkIsInt(pn)):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        conn=classSqlBaseMgr.getInstance(instanceName='probet_oss')
        #1.获取startTime注册账号量及accountId
        if channel:
            ids_sql = "select accountId from dj_regbill WHERE dj_regbill.channel='{}' ".format(channel)
        else:
            ids_sql="select accountId from dj_regbill"

        #更据id，时间获取充值订单，
        sql = "select COUNT(orderId) from dj_paybill WHERE dj_paybill.accountId IN ("+ids_sql+") AND dj_paybill.payTime BETWEEN {} AND {} ".format(startTime,endTime)
        listRest = yield from conn._exeCute(sql)
        count = yield from listRest.fetchone()
        count=count[0]
        sql="select * from dj_paybill WHERE dj_paybill.accountId IN ("+ids_sql+") AND dj_paybill.payTime BETWEEN {} AND {} limit {} offset {}".format(
            startTime,endTime,MSG_PAGE_COUNT,(pn-1)*MSG_PAGE_COUNT)
        listRest=yield from conn._exeCute(sql)
        orders=yield from listRest.fetchall()
        if len(orders)==0:
            return classJsonDump.dumps(objRep)
        for x in orders:
            data=cData()
            data.payTime=x['payTime']
            data.orderId=x['orderId']
            data.accountId=x['accountId']
            data.payCoin="%.2f"%round(x['payCoin']/100,2)
            data.payChannel=x['payChannel']
            data.orderState=x['orderState']
            data.thirdPayOrder=x['thirdPayOrder']
            objRep.data.append(data)
        objRep.count=count
        if pn==1:
            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "充值数据查询",
                'actionTime': getNow(),
                'actionMethod': methodName,
                'actionDetail': "充值数据查询",
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)
