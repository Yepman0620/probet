import asyncio
import json
from sqlalchemy.sql import select
from sqlalchemy import update
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.models import *
import logging
from error.errorCode import errorLogic, exceptionLogic
from lib.ganerateToken import generate_token
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow

class cData():
    def __init__(self):
        self.token = ""
        self.accountId = ""
        self.create_time = 0
        self.role_id = 0
        self.action_names=[]

class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = ""

@asyncio.coroutine
def handleHttp(request:dict):
    # 登陆
    accountId=request.get('accountId','')
    password=request.get('password','')

    if not all([accountId,password]):
        logging.debug(exceptionLogic(errorLogic.client_param_invalid))
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        conn=classSqlBaseMgr.getInstance()
        sql=select([tb_admin]).where(tb_admin.c.accountId==accountId)
        listRest = yield from conn._exeCute(sql)
        objUser=yield from listRest.fetchone()
        if objUser is None:
            logging.debug(errorLogic.wrong_accountId_or_password)
            raise exceptionLogic(errorLogic.wrong_accountId_or_password)
        if not check_password(objUser['passwordHash'],password):
            logging.debug(errorLogic.wrong_accountId_or_password)
            raise exceptionLogic(errorLogic.wrong_accountId_or_password)

        sql=select([tb_role.c.id]).where(tb_role.c.id==objUser['role_id'])
        listRest=yield from conn._exeCute(sql)
        role_id=yield from listRest.fetchone()
        token=generate_token(objUser['accountId'])
        sql=update(tb_admin).where(tb_admin.c.accountId==accountId).values(token=token)
        yield from conn._exeCuteCommit(sql)
        # sql=select([tb_action.c.action_name]).where(tb_action.c.id.in_(select([tb_role_action.c.action_id]).where(tb_role_action.c.role_id==role_id)))
        sql="SELECT dj_admin_action.action_name FROM dj_admin_action WHERE dj_admin_action.id IN (SELECT dj_admin_role_action.action_id FROM dj_admin_role_action WHERE dj_admin_role_action.role_id ={})".format(role_id[0])

        listNames=yield from conn._exeCute(sql)
        objNames=yield from listNames.fetchall()
        action_names=[]
        for x in objNames:
            action_names.append(x['action_name'])
        #构建回包
        resp=cResp()
        data=cData()
        data.accountId=objUser['accountId']
        data.token=token
        data.role_id=objUser['role_id']
        data.create_time=objUser['create_time']
        data.action_names=action_names
        resp.data=data
        resp.ret=errorLogic.success[0]

        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "登录",
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionDetail': "登录",
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(resp)

    except exceptionLogic as e:
        logging.exception(e)
        raise e
    except Exception as e:
        raise e