import asyncio
import ast
import json
from sqlalchemy import select
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.models import *
import logging
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow
from osssvr.utils.models import tb_dj_admin_action_bill


class cData():
    def __init__(self):
        self.phone = ""
        # self.accountId = ""
        # # self.headAddress = ""

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []
        self.count=0

@token_required
@permission_required('用户列表查询')
@asyncio.coroutine
def handleHttp(request: dict):
    # 根据条件查询数据库用户信息
    level=request.get('level','')
    pn=request.get('pn',1)
    try:
        pn = int(pn)
    except Exception as e:
        logging.debug(errorLogic.client_param_invalid)
        raise errorLogic.client_param_invalid

    conn = classSqlBaseMgr.getInstance()
    try:
        sql="select * from dj_account "
        if level:
            sql=sql+"where level={} ".format(level)
        count_sql=sql.replace(r'*','count(accountId)',1)
        list_sql=sql+"order by loginTime desc limit {} offset {}".format(MSG_PAGE_COUNT,(pn-1)*MSG_PAGE_COUNT)
        counRet=yield from conn._exeCute(count_sql)
        countRes=yield from counRet.fetchone()
        resp=cResp()
        resp.count = countRes[0]
        listRet=yield from conn._exeCute(list_sql)
        listRes=yield from listRet.fetchall()

        for user in listRes:
            data=cData()
            data.accountId=user['accountId']
            data.realName=user['realName']
            data.level=user['level']
            data.lastPBCRefreshTime = user['lastPBCRefreshTime']
            data.coin="%.2f"%round(user['coin']/100,2)
            if user['pingboCoin'] is None:
                data.pingboCoin = 0
            else:
                data.pingboCoin="%.2f"%round(user['pingboCoin']/100,2)

            if user['shabaCoin'] is None:
                data.shabaCoin = 0
            else:
                data.shabaCoin="%.2f"%round(user['shabaCoin']/100,2)

            data.phone=user['phone']
            data.userType=user['userType']
            data.loginTime=user['loginTime']
            data.agentId=user['agentId']
            resp.data.append(data)

        if pn==1:
            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "查询用户列表",
                'actionTime': getNow(),
                'actionMethod': methodName,
                'actionDetail': "查询等级为：{} 用户列表".format(level),
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))


        return classJsonDump.dumps(resp)
    except Exception as e:
        logging.debug(e)
        raise e


