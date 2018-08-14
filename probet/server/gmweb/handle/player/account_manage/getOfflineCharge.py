import asyncio
import json

from datawrapper.sqlBaseMgr import classSqlBaseMgr
import logging
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from lib.timehelp.timeHelp import getNow
from logic.logicmgr import checkParamValid as cpv
from lib.jsonhelp import classJsonDump

class cData():
    def __init__(self):
        self.accountId=""

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('线下充值管理')
@asyncio.coroutine
def handleHttp(request: dict):
    # 获取充值账户下的待处理账单
    transTo=request.get('transTo','')
    money=request.get('money','')
    if not transTo:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        conn = classSqlBaseMgr.getInstance()
        if money:
            if cpv.checkIsString(money):
                raise exceptionLogic(errorLogic.client_param_invalid)
            fMoney = float(money)
            if not cpv.checkIsFloat(fMoney):
                raise exceptionLogic(errorLogic.client_param_invalid)
            iCoin = int(fMoney * 100)
            if not cpv.checkIsInt(iCoin):
                raise exceptionLogic(errorLogic.client_param_invalid)

            ids_sql = "select orderId from dj_coin_history WHERE transTo='{}' AND coinNum={} AND tradeState=2 AND tradeType=1 ".format(transTo,iCoin)

        else:
            ids_sql = "select orderId from dj_coin_history WHERE transTo='{}' AND tradeState=2 AND tradeType=1 ".format(transTo)

        sql="select * from dj_pay_order WHERE payOrder IN ("+ids_sql+") and orderTime between {} and {} order by status desc,orderTime desc".format(getNow()-3600*24,getNow())
        listRest=yield from conn._exeCute(sql)
        pay_list=yield from listRest.fetchall()
        resp=cResp()
        for x in pay_list:
            data=cData()
            data.payOrder=x['payOrder']
            data.payChannel=x['payChannel']
            data.accountId=x['accountId']
            data.orderTime=x['orderTime']
            data.buyCoin="%.2f" % round(x['buyCoin'] / 100, 2)
            data.ip=x['ip']
            data.status=x['status']
            resp.data.append(data)

        resp.ret=errorLogic.success[0]

        return classJsonDump.dumps(resp)
    except exceptionLogic as e:
        logging.error(repr(e))
        raise e
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)
