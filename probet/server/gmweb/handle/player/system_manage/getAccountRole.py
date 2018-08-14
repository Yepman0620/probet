import asyncio
import logging
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from datawrapper.sqlBaseMgr import classSqlBaseMgr

class cData():
    def __init__(self):
        self.accounts=[]
        self.roles=[]

class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = {}

@token_required
@permission_required('权限管理')
@asyncio.coroutine
def handleHttp(request:dict):
    try:
        conn=classSqlBaseMgr.getInstance()
        sql="select * from dj_admin_role"
        listRest=yield from conn._exeCute(sql)
        roles=yield from listRest.fetchall()
        sql="select * from dj_admin_account"
        listRest = yield from conn._exeCute(sql)
        accounts = yield from listRest.fetchall()
        resp=cResp()
        data=cData()
        for x in roles:
            dict1={}
            dict1['id'] = x['id']
            dict1['name'] = x['role_name']
            data.roles.append(dict1)

        for x in accounts:
            dict1={}
            dict1['name'] = x['accountId']
            data.accounts.append(dict1)

        resp.data=data
        resp.ret=errorLogic.success[0]
        return classJsonDump.dumps(resp)
    except Exception as e:
        logging.debug(e)
        raise exceptionLogic(errorLogic.db_error)
