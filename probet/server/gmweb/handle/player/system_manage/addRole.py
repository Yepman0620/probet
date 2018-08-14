import asyncio
import json
from sqlalchemy.exc import IntegrityError
from datawrapper.sqlBaseMgr import classSqlBaseMgr
import logging
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow


class cData():
    def __init__(self):
        self.id = ""
        self.accounts = []
        self.role_name = ""
        self.actions = []

class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('权限管理')
@asyncio.coroutine
def handleHttp(request:dict):
    role_name=request.get('role_name','')
    if not role_name:
        logging.debug(exceptionLogic(errorLogic.client_param_invalid))
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        conn=classSqlBaseMgr.getInstance()
        sql="insert into dj_admin_role(role_name) VALUES('{}') ".format(role_name)
        yield from conn._exeCuteCommit(sql)
        sql="select * from dj_admin_role"
        listRest=yield from conn._exeCute(sql)
        roles=yield from listRest.fetchall()
        resp=cResp()
        # 获取详细的角色信息
        for role in roles:
            data = cData()
            data.id = role['id']
            data.role_name = role['role_name']
            sql="select accountId from dj_admin_account WHERE  role_id={}".format(role['id'])
            listRest=yield from conn._exeCute(sql)
            accounts=yield from listRest.fetchall()
            data.accounts = [{"id":x['accountId']} for x in accounts]
            sql="select id,action_name from dj_admin_action WHERE(id IN (select action_id from dj_admin_role_action WHERE role_id={})) ".format(role['id'])
            listRest=yield from conn._exeCute(sql)
            actions=yield from listRest.fetchall()
            data.actions = [{"id":x['id'],"name": x['action_name']} for x in actions]
            resp.data.append(data)

        resp.ret=errorLogic.success[0]
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "新增后台角色",
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionDetail': "新增后台角色：{}".format(role_name),
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(resp)
    except IntegrityError as e:
        logging.debug(e)
        raise exceptionLogic(errorLogic.account_already_exists)
    except Exception as e:
        logging.debug(e)
        raise exceptionLogic(errorLogic.db_error)
