import asyncio
from datawrapper.sqlBaseMgr import classSqlBaseMgr
import logging
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump

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
    if not role_id:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        conn = classSqlBaseMgr.getInstance()
        sql = "select * from dj_admin_account WHERE role_id={}".format(role_id)
        listRest = yield from conn._exeCute(sql)
        accounts = yield from listRest.fetchall()
        resp=cResp()
        # 获取详细的角色信息
        for account in accounts:
            resp.data.append(account['accountId'])

        resp.ret=errorLogic.success[0]
        return classJsonDump.dumps(resp)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)
