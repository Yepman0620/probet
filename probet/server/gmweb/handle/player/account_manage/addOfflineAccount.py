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
@permission_required('线下充值账户管理')
@asyncio.coroutine
def handleHttp(request: dict):
    # 新增线下充值账户
    name=request.get('name','')
    cardId=request.get('cardId','')
    bank=request.get('bank','')
    kind=request.get('kind','')
    bankInfo=request.get('bankInfo','')
    if not all([name,cardId,kind]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        conn = classSqlBaseMgr.getInstance()
        sql="insert into dj_offline_account_recharge(name,accountId,bank,kind,status,bankInfo) VALUES('{}','{}','{}','{}',0,'{}') ".format(name,cardId,bank,kind,bankInfo)
        yield from conn._exeCuteCommit(sql)

        resp=cResp()
        sql = "select * from dj_offline_account_recharge"
        listRest=yield from conn._exeCute(sql)
        accounts=yield from listRest.fetchall()
        for x in accounts:
            data=cData()
            data.id=x['id']
            data.name=x['name']
            data.status=x['status']
            data.accountId=x['accountId']
            data.bank=x['bank']
            data.kind=x['kind']
            data.bankInfo=x['bankInfo']
            resp.data.append(data)

        fileName=__name__
        nameList=fileName.split('.')
        methodName=nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId',''),
            'action': "新增线下充值账号",
            'actionTime': getNow(),
            'actionMethod':methodName,
            'actionDetail': "新增线下充值账号:{},账号姓名为：{}".format(cardId,name),
            'actionIp':request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(resp)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)

