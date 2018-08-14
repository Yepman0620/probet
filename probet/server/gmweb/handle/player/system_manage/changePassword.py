import asyncio
import json
from gmweb.utils.models import *
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
    # 修改密码
    accountId=request.get('accountId','')
    oldPassword=request.get('oldPassword','')
    password=request.get('password','')
    rePassword=request.get('rePassword','')

    if not all([accountId,password,rePassword]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    if password!=rePassword:
        logging.debug(errorLogic.login_pwd_not_valid)
        raise exceptionLogic(errorLogic.login_pwd_not_valid)

    if len(password)<6 or len(password)>20:
        logging.debug(errorLogic.player_TradePwd_length_out_of_range)
        raise exceptionLogic(errorLogic.player_TradePwd_length_out_of_range)


    try:
        conn=classSqlBaseMgr.getInstance()
        sql="select passwordHash from dj_admin_account WHERE accountId='{}'".format(accountId)
        listRest=yield from conn._exeCute(sql)
        old_pwd=yield from listRest.fetchone()

        if not check_password(old_pwd['passwordHash'],oldPassword):
            logging.debug(errorLogic.login_only_old_pwd_not_valid)
            raise exceptionLogic(errorLogic.login_only_old_pwd_not_valid)

        sql="update dj_admin_account set passwordHash='{}' WHERE accountId='{}'".format(generate_password_hash(password),accountId)
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
            'action': "修改自己密码",
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionDetail': "修改自己密码",
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))

        return classJsonDump.dumps(resp)
    except exceptionLogic as e :
        raise e
    except Exception as e:
        logging.debug(e)
        raise exceptionLogic(errorLogic.db_error)