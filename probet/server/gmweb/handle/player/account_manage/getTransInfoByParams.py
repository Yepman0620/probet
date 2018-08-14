import asyncio
import json
from datawrapper.sqlBaseMgr import classSqlBaseMgr
import logging
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow
import ast

class cData():
    def __init__(self):
        self.accountId = ""
        self.bankCard=None
class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('充值明细')
@asyncio.coroutine
def handleHttp(request: dict):
    # 根据条件查询数据库用户交易记录
    userId=request.get('userId','')
    phone=request.get('phone','')
    email=request.get('email','')
    #交易类型
    pageNum=request.get('pageNum',1)
    kind=request.get('kind','')
    # 单号
    payOrder=request.get('payOrder','')
    # 交易渠道
    channel=request.get('channel','')
    startTime=request.get('startTime',0)
    endTime=request.get('endTime',0)
    if (not startTime) and (not endTime):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        pageNum=int(pageNum)
    except Exception as e:
        logging.debug(errorLogic.client_param_invalid)
        raise errorLogic.client_param_invalid
    if kind not in ["recharge","transfer","withdrawal","rebate"]:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    if not all([startTime,endTime]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        conn = classSqlBaseMgr.getInstance()
        if payOrder:
            base_sql="select orderId from dj_coin_history WHERE orderId='{}'".format(payOrder)
        else:
            accountId=None
            if userId:
                accountId = userId
            elif phone:
                sql="select accountId from dj_account WHERE phone='{}'".format(phone)
                listRest=yield from conn._exeCute(sql)
                accountId=yield from listRest.fetchone()
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
                accountId = accountId[0]

            sql = "select orderId from dj_coin_history WHERE accountId='{}'".format(accountId)
            base_sql=sql+" AND orderTime BETWEEN {} AND {}".format(startTime,endTime)
            if not accountId:
                sql = "select orderId from dj_coin_history"
                base_sql = sql + " where orderTime BETWEEN {} AND {}".format(startTime, endTime)

        if kind == 'recharge':
            # 充值记录
            his_coin_sql=base_sql+" AND tradeType=1 "
            if channel:
                #获取指定查询渠道的单号
                pay_info_sql="select payOrder from dj_pay_order WHERE payChannel='{}'".format(channel)
                pay_info_sql=pay_info_sql+" AND payOrder IN ("+his_coin_sql+")"
            else:
                # 全部
                pay_info_sql = his_coin_sql
            his_coin_sql="select orderId from dj_coin_history WHERE orderId IN ("+pay_info_sql+") order by orderTime desc"
        elif kind == 'transfer':
            # 转账记录
            his_coin_sql = base_sql + " AND tradeType=3 order by orderTime desc"
        elif kind=='withdrawal':
            # 提款
            his_coin_sql = base_sql + " AND tradeType=2 order by orderTime desc"
        else:
            pass


        coun_sql=his_coin_sql.replace(r'orderId','count(orderId)',1)
        listRest=yield from conn._exeCute(coun_sql)
        count=yield from listRest.fetchone()
        count=count[0]

        sql=his_coin_sql.replace(r'orderId','*',1)
        sql=sql+" limit {} offset {}".format(MSG_PAGE_COUNT, (pageNum - 1) * MSG_PAGE_COUNT)
        listRest = yield from conn._exeCute(sql)
        his_coin = yield from listRest.fetchall()
        resp = cResp()
        actionbill_accountId=''
        for x in his_coin:
            data = cData()
            data.orderTime = x['orderTime']
            actionbill_accountId=x['accountId']
            data.accountId = x['accountId']
            data.orderId=x['orderId']
            if kind=='recharge':
                data.payChannel = x['transFrom']
                sql="select thirdPayOrder,thirdPayName from dj_pay_order WHERE payOrder='{}'".format(x['orderId'])
                orderRet=yield from conn._exeCute(sql)
                orderRes=yield from orderRet.fetchone()
                data.thirdPayOrder = orderRes[0]
                data.thirdPayName = orderRes[1]
            
            elif kind=='withdrawal':
                #提款
                sql="select realName,bankcard from dj_account WHERE accountId='{}'".format(x['accountId'])
                userInfoRes=yield from conn._exeCute(sql)
                userInfoRet=yield from userInfoRes.fetchone()
                data.bankOrderId=x['bankOrderId']
                data.realName=userInfoRet[0]
                bankCardInfoList =ast.literal_eval(userInfoRet[1])
                for bankcard in bankCardInfoList:
                    if bankcard['cardNum']==x['transTo']:
                        data.bankCard=bankcard
            else:
                data.orderId , data.payChannel, data.thirdPayOrder, thirdPayName ='','','',''

            data.endTime=x['endTime']
            data.transTo = x['transTo']
            data.coinNum = "%.2f" % round(x['coinNum'] / 100, 2)
            data.tradeState = x['tradeState']
            data.reviewer = x['reviewer'] if kind != 'transfer' else ''
            data.reason=x['reason']
            data.transOut = x['transFrom']
            resp.data.append(data)
        resp.count=count
        resp.ret = errorLogic.success[0]
        if pageNum==1:
            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "查询交易记录",
                'actionTime': getNow(),
                'actionMethod': methodName,
                'actionDetail': "查询用户：{}交易记录".format(actionbill_accountId),
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))

        return classJsonDump.dumps(resp)

    except exceptionLogic as e:
        logging.error(repr(e))
        raise e
    except Exception as e:
        logging.debug(e)
        raise exceptionLogic(errorLogic.db_error)
