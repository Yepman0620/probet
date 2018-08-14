import asyncio
import json
from gmweb.utils.models import *
import logging
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from lib.timehelp.timeHelp import getNow


class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = ""

@token_required
@permission_required('修改密码')
@asyncio.coroutine
def handleHttp(request:dict):
    userId=request.get('userId','')
    password=request.get('password','')

    if not all([userId,password]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    if len(password)<6 or len(password)>20:
        logging.debug(errorLogic.player_TradePwd_length_out_of_range)
        raise exceptionLogic(errorLogic.player_TradePwd_length_out_of_range)

    try:
        conn=classSqlBaseMgr.getInstance()
        sql="update dj_admin_account set passwordHash='{}' WHERE accountId='{}'".format(generate_password_hash(password),userId)
        yield from conn._exeCuteCommit(sql)

        resp=cResp()
        resp.ret=errorLogic.success[0]
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "修改用户密码",
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionDetail': "修改后台用户:{}密码".format(userId),
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
