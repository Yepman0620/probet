import asyncio
import json
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.models import *
import logging
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow


class cData():
    def __init__(self):
        self.id=0
        self.role_name=''
        self.accounts=[]
        self.actions=[]

class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('权限管理')
@asyncio.coroutine
def handleHttp(request:dict):
    role_id=request.get('role_id','')
    action_names=request.get('action_names',[])
    if not all([role_id]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:

        conn = classSqlBaseMgr.getInstance()
        sql = "select count(role_id) from dj_admin_role_action WHERE role_id={}".format(role_id)
        listRest=yield from conn._exeCute(sql)
        count=yield from listRest.fetchone()
        if count[0]:
            # 有数据
            if len(action_names)==0:
                sql="delete from dj_admin_role_action WHERE role_id={}".format(role_id)
                yield from conn._exeCuteCommit(sql)
            else:
                sql = "delete from dj_admin_role_action WHERE role_id={}".format(role_id)
                yield from conn._exeCuteCommit(sql)
                for x in action_names:
                    sql = "select id from dj_admin_action WHERE action_name='{}'".format(x)
                    listRest = yield from conn._exeCute(sql)
                    action_id = yield from listRest.fetchone()
                    sql="insert into dj_admin_role_action VALUES ('{}','{}')".format(role_id,action_id[0])
                    yield from conn._exeCuteCommit(sql)
        else:
            # 没数据
            yield from conn._exeCuteCommit(sql)
            for x in action_names:
                sql="select id from dj_admin_action WHERE action_name='{}'".format(x)
                listRest=yield from conn._exeCute(sql)
                action_id=yield from listRest.fetchone()
                sql = "insert into dj_admin_role_action VALUES ('{}','{}')".format(role_id, action_id[0])
                yield from conn._exeCuteCommit(sql)

        resp=cResp()
        sql = "select * from dj_admin_role"
        listRest = yield from conn._exeCute(sql)
        roles = yield from listRest.fetchall()
        # 获取详细的角色信息
        for role in roles:
            data = cData()
            data.id = role['id']
            data.role_name = role['role_name']
            sql = "select accountId from dj_admin_account WHERE role_id={}".format(role['id'])
            listRest = yield from conn._exeCute(sql)
            accounts = yield from listRest.fetchall()
            data.accounts = [{"id": x['accountId']} for x in accounts]

            sql = "select id,action_name from dj_admin_action WHERE (id IN (SELECT action_id FROM dj_admin_role_action WHERE role_id={}))".format(role['id'])
            listRest = yield from conn._exeCute(sql)
            actions = yield from listRest.fetchall()

            data.actions = [{"id": x['id'], "name": x['action_name']} for x in actions]
            resp.data.append(data)

        resp.ret=errorLogic.success[0]
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "修改角色权限",
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionDetail': "修改角色id：{}权限".format(role_id),
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(resp)
    except Exception as e:
        logging.debug(e)
        raise exceptionLogic(errorLogic.db_error)