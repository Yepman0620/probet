import asyncio
from datawrapper.sqlBaseMgr import classSqlBaseMgr
import logging
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump

class cData():
    def __init__(self):
        self.id=0
        self.action_name=''

class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('权限管理')
@asyncio.coroutine
def handleHttp(request:dict):
    try:
        conn = classSqlBaseMgr.getInstance()
        sql = "select * from dj_admin_action"
        listRest = yield from conn._exeCute(sql)
        actions = yield from listRest.fetchall()

        resp=cResp()

        for action in actions:
            data=cData()
            data.id=action['id']
            data.action_name=action['action_name']
            resp.data.append(data)

        resp.ret=errorLogic.success[0]
        return classJsonDump.dumps(resp)
    except Exception as e:
        logging.debug(e)
        raise exceptionLogic(errorLogic.db_error)
