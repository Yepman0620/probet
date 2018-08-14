import asyncio
import json
import logging
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required, permission_required
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from lib.timehelp.timeHelp import getNow


class cData():
    def __init__(self):
        self.id = 0
        self.accountId = ""
        self.role_name = ""

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('用户管理')
@asyncio.coroutine
def handleHttp(request:dict):
    delId=request.get('id','')
    if not delId:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        conn=classSqlBaseMgr.getInstance()
        sql="delete from dj_admin_account WHERE id={}".format(delId)
        yield from conn._exeCuteCommit(sql)

        sql="select count(id) from dj_admin_account"
        listRest=yield from conn._exeCute(sql)
        count=yield from listRest.fetchone()

        sql="select * from dj_admin_account order by dj_admin_account.id limit {}".format(MSG_PAGE_COUNT)
        listRest=yield from conn._exeCute(sql)
        accounts=yield from listRest.fetchall()
        resp = cResp()
        for x in accounts:
            data = cData()
            data.id = x['id']
            data.accountId = x['accountId']
            if x['role_id'] is None:
                data.role_name = ''
            else:
                sql = "select dj_admin_role.role_name from dj_admin_role WHERE dj_admin_role.id={}".format(x['role_id'])
                listRest = yield from conn._exeCute(sql)
                role_name = yield from listRest.fetchone()
                data.role_name = role_name[0]
            resp.data.append(data)

        resp.count=count[0]
        resp.ret=errorLogic.success[0]
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "删除后台账号",
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionDetail': "删除后台账号：{}".format(delId),
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
