import asyncio
import json
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.tools import token_required, permission_required
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow
from logic.logicmgr.checkParamValid import checkIsInt

class cData():
    def __init__(self):
        self.time=0             #日期
        self.accountId=''       #账号
        self.roleName=''        #角色分组
        self.logDetail=0        #日志详情

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []
        self.count=0

@token_required
@permission_required('日志查询')
@asyncio.coroutine
def handleHttp(request: dict):
    """查询日志数据"""
    adminAccount = request.get('adminAccount', '')
    startTime = request.get('startTime', 0)
    endTime = request.get('endTime', 0)
    pn=request.get('pn',1)
    try:
        pn=int(pn)
    except Exception as e:
        logging.error(repr(e))
        raise exceptionLogic(errorLogic.client_param_invalid)
    objRep = cResp()

    if not all([startTime,endTime]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    if (not checkIsInt(startTime)) or (not checkIsInt(endTime)):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    log_sql="select * from dj_admin_action_bill WHERE actionTime BETWEEN {} AND {} ".format(startTime,endTime)
    if adminAccount:
        log_sql=log_sql+"and accountId='{}' ".format(adminAccount)
    log_count_sql=log_sql.replace(r'*','count(id)',1)
    try:
        with (yield from classSqlBaseMgr.getInstance(instanceName='probet_oss').objDbMysqlMgr) as conn:
            countRet=yield from conn.execute(log_count_sql)
            count=yield from countRet.fetchone()
            objRep.count=count[0]
            log_sql=log_sql+"order by actionTime desc limit {} offset {}".format(MSG_PAGE_COUNT, (pn - 1) * MSG_PAGE_COUNT)
            logRet=yield from conn.execute(log_sql)
            logList=yield from logRet.fetchall()
            probet_conn = classSqlBaseMgr.getInstance()
            for x in logList:
                data=cData()
                data.accountId=x['accountId']
                data.time=x['actionTime']
                data.logDetail=x['actionDetail']
                role_name_sql="select role_name from dj_admin_role WHERE id=(SELECT role_id FROM dj_admin_account WHERE accountId='{}')".format(x['accountId'])
                roleNameRet=yield from probet_conn._exeCute(role_name_sql)
                roleNameList=yield from roleNameRet.fetchone()
                data.roleName="该管理员不在系统中" if roleNameList is None else roleNameList[0]
                objRep.data.append(data)
        if pn==1:
            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "查询日志数据",
                'actionTime': getNow(),
                'actionMethod': methodName,
                'actionDetail': "查询日志数据",
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)
