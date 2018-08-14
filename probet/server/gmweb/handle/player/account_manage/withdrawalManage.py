import asyncio
import json
import logging
import ast
from lib.timehelp.timeHelp import getNow
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump


class cData():
    def __init__(self):
        self.orderId=''     #单号
        self.accountId=''   #用户名
        self.userType=''    #用户类型1.普通用户2.代理
        self.orderTime=0    #申请时间
        self.coinNum=0      #申请金额
        self.bankCardNum='' #银行卡号
        self.bankCardName=''#银行卡号姓名
        self.endTime=0      #处理时间
        self.tradeStatus=1  #订单状态1.成功2.等待
        self.bankCard=None

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('用户提款管理')
@asyncio.coroutine
def handleHttp(request: dict):
    # 用户、代理提款接口
    userId=request.get('userId','')
    startTime=request.get('startTime',0)
    endTime=request.get('endTime',0)
    kind=request.get('kind','')
    pn=request.get('pn',1)

    try:
        pn=int(pn)
    except Exception as e:
        logging.error(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    if not all([startTime,endTime]):
        logging.error(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    base_sql="select * from dj_coin_history WHERE orderTime BETWEEN {} AND {} AND tradeType=2 and tradeState=2 ".format(startTime,endTime)
    if (not userId) and (not kind):
        base_sql = base_sql + "order by orderTime desc "

    objResp=cResp()
    conn=classSqlBaseMgr.getInstance()
    try:
        userType_sql=None
        if userId:
            # 填写了用户名
            base_sql = base_sql + "AND accountId='{}' order by orderTime desc ".format(userId)
            userType_sql="select userType,realName from dj_account WHERE accountId='{}' ".format(userId)
        else:
            if kind:
                #选择了类型
                if kind not in ['agent','user']:
                    logging.error(errorLogic.client_param_invalid)
                    raise exceptionLogic(errorLogic.client_param_invalid)
                accountIds_sql=base_sql.replace(r'*','DISTINCT(accountId)',1)

                if kind=='agent':
                    #代理
                    agentIds_sql="select accountId from dj_account WHERE userType=2 AND accountId IN ("+accountIds_sql+") "
                else:
                    #普通用户
                    agentIds_sql = "select accountId from dj_account WHERE userType=1 AND accountId IN ("+accountIds_sql+") "

                base_sql=base_sql+" AND accountId in ("+agentIds_sql+") order by orderTime desc "

        if userType_sql is not None:
            userInfo=yield from conn._exeCute(userType_sql)
            userInfoTuple=yield from userInfo.fetchone()
        count_sql=base_sql.replace(r'*','COUNT(orderId)',1)
        countRet=yield from conn._exeCute(count_sql)
        count=yield from countRet.fetchone()
        objResp.count=count[0]
        base_sql=base_sql+"limit {} offset {}".format(MSG_PAGE_COUNT,(pn-1)*MSG_PAGE_COUNT)
        listRet=yield from conn._exeCute(base_sql)
        orderList=yield from listRet.fetchall()
        for x in orderList:
            data=cData()
            data.orderId=x['orderId']
            data.accountId=x['accountId']
            data.orderTime=x['orderTime']
            data.coinNum="%.2f"%round(x['coinNum']/100,2)
            data.tradeStatus=x['tradeState']
            data.bankCardNum = x['transTo']
            data.endTime=x['endTime']
            data.reviewer=x['reviewer']
            if userId:
                data.userType=userInfoTuple[0]
                data.bankCardName=userInfoTuple[1]
            else:
                sql="select userType,realName,bankcard from dj_account WHERE accountId='{}' ".format(x['accountId'])
                userRet = yield from conn._exeCute(sql)
                userRetList = yield from userRet.fetchone()
                data.userType=userRetList[0]
                data.bankCardName=userRetList[1]
                bankCardInfoList = ast.literal_eval(userRetList[2])
                for bankcard in bankCardInfoList:
                    if bankcard['cardNum'] == x['transTo']:
                        data.bankCard = bankcard

            objResp.data.append(data)
        if pn==1:
            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "获取用户提款信息",
                'actionTime': getNow(),
                'actionMethod': methodName,
                'actionDetail': "查询用户:{},提款信息".format(userId),
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(objResp)
    except Exception as e :
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)

