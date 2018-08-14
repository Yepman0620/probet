import asyncio
import json
from datawrapper.sqlBaseMgr import classSqlBaseMgr
import logging
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow,sevenDayTimestamp

class cData():
    def __init__(self):
        self.accountId = ""

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('反水记录')
@asyncio.coroutine
def handleHttp(request: dict):
    # 根据条件查询数据库反水记录
    userId=request.get('userId','')
    phone=request.get('phone','')
    email=request.get('email','')
    pn=request.get('pn',1)
    # 单号
    payOrder=request.get('payOrder','')
    # 交易渠道
    channel=request.get('channel','')
    startTime=request.get('startTime',sevenDayTimestamp())
    endTime=request.get('endTime',getNow())

    try:
        pn=int(pn)
    except Exception as e:
        logging.debug(errorLogic.client_param_invalid)
        raise errorLogic.client_param_invalid

    try:
        conn = classSqlBaseMgr.getInstance()
        if payOrder:
            sql = "select * from dj_coin_history WHERE orderId='{}' AND tradeType=7".format(payOrder)
        else:
            accountId=None
            if userId:
                accountId = userId
            elif phone:
                sql = "select accountId from dj_account WHERE phone='{}'".format(phone)
                listRest = yield from conn._exeCute(sql)
                accountId = yield from listRest.fetchone()
                if accountId is None:
                    logging.debug(errorLogic.player_data_not_found)
                    raise exceptionLogic(errorLogic.player_data_not_found)
                accountId=accountId[0]
            elif email:
                sql = "select accountId from dj_account WHERE email='{}'".format(email)
                listRest = yield from conn._exeCute(sql)
                accountId = yield from listRest.fetchone()
                if accountId is None:
                    logging.debug(errorLogic.player_data_not_found)
                    raise exceptionLogic(errorLogic.player_data_not_found)
                accountId=accountId[0]

            sql = "select * from dj_coin_history WHERE accountId='{}' AND tradeType=7".format(accountId)
            if not accountId:
                sql="select * from dj_coin_history WHERE tradeType=7"

        base_sql = sql + " AND orderTime BETWEEN {} AND {}".format(startTime, endTime)

        if channel:
            sql = "select payOrder from dj_pay_order WHERE payChannel='{}' AND accountId='{}' ".format(channel,accountId)
            sql = base_sql+" AND orderId in ("+sql+") order by orderTime desc"
        else:
            sql=base_sql+" order by orderTime desc"

        listRest=yield from conn._exeCute(sql.replace(r'*','count(orderId)'))
        notes=yield from listRest.fetchone()
        count=notes[0]
        listRest=yield from conn._exeCute(sql+" limit {} offset {} ".format(MSG_PAGE_COUNT,(pn-1)*MSG_PAGE_COUNT))
        notes=yield from listRest.fetchall()

        resp=cResp()
        for x in notes:
            data=cData()
            data.accountId=x['accountId']
            data.orderId=x['orderId']
            data.coinNum=x['coinNum']
            data.validWater="%.2f"%round(x['validWater']/100,2)
            data.tradeState=x['tradeState']
            data.orderTime=x['orderTime']
            data.reviewer=x['reviewer']
            resp.data.append(data)
        resp.ret = errorLogic.success[0]
        resp.count=count
        if pn==1:
            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "查询用户反水记录",
                'actionTime': getNow(),
                'actionMethod': methodName,
                'actionDetail': "查询用户：{} 反水记录".format(accountId),
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))

        return classJsonDump.dumps(resp)

    except exceptionLogic as e:
        logging.exception(e)
        raise e
    except Exception as e:
        logging.debug(e)
        raise exceptionLogic(errorLogic.db_error)
