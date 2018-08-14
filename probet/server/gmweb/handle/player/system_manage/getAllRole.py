import asyncio
from datawrapper.sqlBaseMgr import classSqlBaseMgr
import logging
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump

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
    kind=request.get('kind','')
    if kind not in ['simple','full']:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        conn = classSqlBaseMgr.getInstance()
        sql = "select * from dj_admin_role"
        listRest = yield from conn._exeCute(sql)
        roles = yield from listRest.fetchall()
        resp=cResp()
        if kind=='simple':
            # 获取简单的角色信息
            for role in roles:
                data=[]
                data.append(role['id'])
                data.append(role['role_name'])
                resp.data.append(data)
        else:
            # 获取详细的角色信息
            for role in roles:
                data=cData()
                data.id=role['id']
                data.role_name=role['role_name']

                sql = "select * from dj_admin_account WHERE role_id={}".format(role['id'])
                listRest = yield from conn._exeCute(sql)
                accounts = yield from listRest.fetchall()
                data.accounts = [{"id":x['accountId']} for x in accounts]

                sql = "select * from dj_admin_action WHERE (id IN (SELECT action_id FROM dj_admin_role_action WHERE role_id={}))".format(role['id'])
                listRest = yield from conn._exeCute(sql)
                actions = yield from listRest.fetchall()
                data.actions = [{"id":x['id'],"name":x['action_name']} for x in actions]
                resp.data.append(data)

        resp.ret=errorLogic.success[0]
        return classJsonDump.dumps(resp)
    except Exception as e:
        logging.debug(e)
        raise exceptionLogic(errorLogic.db_error)
