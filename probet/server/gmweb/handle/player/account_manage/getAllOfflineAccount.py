import asyncio
import json
from datawrapper.sqlBaseMgr import classSqlBaseMgr
import logging
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow


class cData():
    def __init__(self):
        self.id = ""
        self.name=""
        self.accountId=""
        self.bank=""
        self.status=""
        self.kind=""

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('线下充值管理')
@asyncio.coroutine
def handleHttp(request: dict):
    # 获取所有线下充值账户
    kind=request.get('kind','')

    try:
        conn = classSqlBaseMgr.getInstance()
        if kind=="all":
            sql = "select * from dj_offline_account_recharge"
        else:
            sql = "select * from dj_offline_account_recharge WHERE kind={}".format(kind)

        listRest = yield from conn._exeCute(sql)
        accounts = yield from listRest.fetchall()
        resp=cResp()
        if len(accounts)==0:
            return classJsonDump.dumps(resp)

        for x in accounts:
            data = cData()
            data.id = x['id']
            data.name = x['name']
            data.status = x['status']
            data.accountId = x['accountId']
            data.kind = x['kind']
            data.bank=x['bank']
            data.bankInfo=x['bankInfo']
            resp.data.append(data)

        if kind=='all':
            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "获取所有线下充值账号",
                'actionTime': getNow(),
                'actionMethod': methodName,
                'actionDetail': "查询所有线下充值账号",
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(resp)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)
