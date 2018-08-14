import asyncio
import json
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from sqlalchemy.exc import IntegrityError
from gmweb.utils.models import *
from gmweb.utils.tools import token_required,permission_required
import logging
from error.errorCode import errorLogic, exceptionLogic
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow
from logic.regex.precompile import NormalCharRegex
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
    # 新增用户
    userId=request.get('userId','')
    password=request.get('password','')
    rePassword=request.get('rePassword','')
    role_id=request.get('role_id',3)

    if not all([userId,password,rePassword,role_id]):
        logging.debug(exceptionLogic(errorLogic.client_param_invalid))
        raise exceptionLogic(errorLogic.client_param_invalid)

    if password!=rePassword:
        logging.debug(exceptionLogic(errorLogic.client_param_invalid))
        raise exceptionLogic(errorLogic.client_param_invalid)

    retU=NormalCharRegex.match(userId)
    if retU is None:
        raise exceptionLogic(errorLogic.user_account_format_not_valid)

    if len(password)<6 or len(password)>20:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    sql="insert into dj_admin_account(accountId,passwordHash,role_id) values('{}','{}',{})".format(userId,generate_password_hash(password),role_id)
    try:
        conn=classSqlBaseMgr.getInstance()
        yield from conn._exeCuteCommit(sql)

        count_sql="select count(dj_admin_account.id) from dj_admin_account"
        listRest=yield from conn._exeCute(count_sql)
        count=yield from listRest.fetchone()
        sql="select * from dj_admin_account limit {}".format(MSG_PAGE_COUNT)
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
        resp.ret = errorLogic.success[0]
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "新增后台用户",
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionDetail': "新增后台用户：{}".format(userId),
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))

        return classJsonDump.dumps(resp)

    except IntegrityError as e:
        logging.debug(e)
        raise exceptionLogic(errorLogic.account_already_exists)
    except Exception as e:
        logging.debug(e)
        raise exceptionLogic(errorLogic.account_already_exists)
