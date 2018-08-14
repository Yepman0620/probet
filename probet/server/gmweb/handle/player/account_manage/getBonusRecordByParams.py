import asyncio
import json
from datawrapper.sqlBaseMgr import classSqlBaseMgr
import logging
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow

class cData():
    def __init__(self):
        self.accountId = ""

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []
        self.count=0

@token_required
@permission_required('红利记录')
@asyncio.coroutine
def handleHttp(request: dict):
    # 根据条件查询数据库用户红利记录
    userId=request.get('userId','')
    email=request.get('email','')
    phone=request.get('phone','')
    startTime=request.get('startTime',0)
    endTime=request.get('endTime',0)
    pn=request.get('pn',1)
    if not all([startTime,endTime]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        pn=int(pn)
        conn = classSqlBaseMgr.getInstance()
        resp=cResp()
        sql=None
        if userId:
            sql = "select accountId from dj_account WHERE dj_account.accountId='{}' ".format(userId)

        elif email:
            sql = "select accountId from dj_account WHERE dj_account.email='{}' ".format(email)

        elif phone:
            sql = "select accountId from dj_account WHERE dj_account.phone='{}' ".format(phone)

        bonus_sql="select * from dj_coin_history WHERE accountId=({}) AND tradeType=9 AND orderTime BETWEEN {} AND {} ".format(sql,startTime,endTime)
        if sql is None:
            bonus_sql = "select * from dj_coin_history WHERE tradeType=9 AND orderTime BETWEEN {} AND {} order by orderTime DESC ".format(startTime, endTime)

        bonus_count_sql=bonus_sql.replace(r'*','count(orderId)',1)
        countRet=yield from conn._exeCute(bonus_count_sql)
        count=yield from countRet.fetchone()
        resp.count=count[0]
        bonus_page_sql=bonus_sql+"limit {} offset {}".format(MSG_PAGE_COUNT,(pn-1)*MSG_PAGE_COUNT)
        bonusRet=yield from conn._exeCute(bonus_page_sql)
        bonusList=yield from bonusRet.fetchall()
        for x in bonusList:
            data=cData()
            data.accountId=x['accountId']
            data.orderId=x['orderId']
            data.active=x['transFrom']
            data.coin="%.2f"%round(x['coinNum']/100,2)
            data.status=x['tradeState']
            data.startTime=x['orderTime']
            data.endTime=x['endTime']
            data.reviewer=x['reviewer']
            resp.data.append(data)

        if pn==1:
            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "查询红利信息",
                'actionTime': getNow(),
                'actionMethod': methodName,
                'actionDetail': "查询用户：{}，红利信息".format(userId),
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(resp)
    except Exception as e:
        logging.debug(e)
        raise e


