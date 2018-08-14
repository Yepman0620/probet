import asyncio
import json
import logging
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required
from lib.jsonhelp import classJsonDump
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from lib.timehelp.timeHelp import getNow


class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = ""

@token_required
@asyncio.coroutine
def handleHttp(request:dict):
    # 登出
    accountId=request.get('accountId','')
    try:
        conn=classSqlBaseMgr.getInstance()
        sql="update dj_admin_account set token='{}' where accountId='{}'".format('',accountId)
        yield from conn._exeCute(sql)
        #构建回包
        resp=cResp()
        resp.ret=errorLogic.success[0]
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "登出",
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionDetail': "登出",
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(resp)

    except Exception as e:
        logging.debug(e)
        raise exceptionLogic(errorLogic.db_error)