import asyncio
import json

from datawrapper.sqlBaseMgr import classSqlBaseMgr
import logging
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from lib.constants import MSG_PAGE_COUNT
from lib.timehelp.timeHelp import getNow
from logic.logicmgr import checkParamValid as cpv
from lib.jsonhelp import classJsonDump

class cData():
    def __init__(self):
        self.accountId=""

class cResp():
    def __init__(self):
        self.count=0
        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('已取消线下订单管理')
@asyncio.coroutine
def handleHttp(request: dict):
    # 获取充值账户下的取消、超时账单
    pn=request.get('pn',1)
    try:
        pn=int(pn)
    except Exception as e:
        logging.debug(repr(e))
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        yield from asyncio.sleep(1)
        conn = classSqlBaseMgr.getInstance()
        #获取取消的订单，未取消，但是超过24小时的订单
        base_sql = "select * from dj_coin_history WHERE tradeState=3 AND tradeType=1 union select * from dj_coin_history WHERE tradeState=2 AND tradeType=1 AND dj_coin_history.orderTime<={} order by orderTime DESC ".format(getNow()-24*3600)
        count_sql='select count(orderId) from '+'('+base_sql+')'+'as h'
        orders_sql=base_sql+"limit {} offset {}".format(MSG_PAGE_COUNT,(pn-1)*MSG_PAGE_COUNT)
        listRest=yield from conn._exeCute(orders_sql)
        pay_list=yield from listRest.fetchall()
        countRet=yield from conn._exeCute(count_sql)
        count=yield from countRet.fetchall()
        resp=cResp()
        resp.count=count[0][0]
        for x in pay_list:
            data=cData()
            data.payOrder=x['orderId']
            data.payChannel=x['transFrom']
            data.accountId=x['accountId']
            data.orderTime=x['orderTime']
            data.buyCoin="%.2f" % round(x['coinNum'] / 100, 2)
            data.reviewer=x['reviewer']
            data.endTime=x['endTime']
            data.reason=x['reason']
            resp.data.append(data)

        if pn==1:
            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "查询已取消/超时线下支付订单",
                'actionTime': getNow(),
                'actionMethod': methodName,
                'actionDetail': "查询已取消/超时线下支付订单",
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))

        return classJsonDump.dumps(resp)

    except Exception as e:
        logging.debug(e)
        raise e
