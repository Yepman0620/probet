import asyncio
import ast
import json
from sqlalchemy import select
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.handle.pinbo.get_player_info import get_pingbo_player_info
from gmweb.utils.models import *
import logging
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required, getAddressByIp
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow
from osssvr.utils.models import tb_dj_admin_action_bill


class cData():
    def __init__(self):
        self.phone = ""
        # self.accountId = ""
        # # self.headAddress = ""

class UserLogData():
    def __init__(self):
        self.time=0
        self.adminAccount=''
        self.roleName=''
        self.detail=''

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []
        self.logData=[]

@token_required
@permission_required('基本信息查询')
@asyncio.coroutine
def handleHttp(request: dict):
    # 根据条件查询数据库用户信息
    userId=request.get('userId','')
    email=request.get('email','')
    phone=request.get('phone','')
    pn = request.get('pn', 1)
    kind=request.get('kind','')

    if kind not in ['like','exact']:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        pn = int(pn)
    except Exception as e:
        logging.debug(errorLogic.client_param_invalid)
        raise errorLogic.client_param_invalid

    conn = classSqlBaseMgr.getInstance()
    try:
        sql=None
        if kind=='like':
            if userId:
                sql=select([tb_dj_account]).where(tb_dj_account.c.accountId.like('%'+userId+'%'))
                # sql="select * from dj_account WHERE accountId LIKE '{}'".format('%'+userId+'%')
            if email:
                sql = select([tb_dj_account]).where(tb_dj_account.c.email.like('%' + email + '%'))
                # sql = "select * from dj_account WHERE email LIKE '{}'".format('%' + email + '%')
            if phone:
                # sql = "select * from dj_account WHERE phone LIKE '{}'".format('%' + phone + '%')
                sql = select([tb_dj_account]).where(tb_dj_account.c.phone.like('%' + phone + '%'))

            if sql is None:
                logging.debug(errorLogic.player_data_not_found)
                raise exceptionLogic(errorLogic.player_data_not_found)

            listRest = yield from conn._exeCute(sql.limit(MSG_PAGE_COUNT).offset((pn - 1) * MSG_PAGE_COUNT))
            users = yield from listRest.fetchall()
        else:
            if userId:
                sql = "select * from dj_account WHERE accountId='{}'".format(userId)

            if email:
                sql = "select * from dj_account WHERE email='{}'".format(email)

            if phone:
                sql = "select * from dj_account WHERE phone='{}'".format(phone)

            if sql is None:
                logging.debug(errorLogic.player_data_not_found)
                raise exceptionLogic(errorLogic.player_data_not_found)

            a_sql=sql+" limit {} offset {}".format(MSG_PAGE_COUNT,(pn-1)*MSG_PAGE_COUNT)
            listRest = yield from conn._exeCute(a_sql)
            users = yield from listRest.fetchall()

        #todo 可以优化但是模糊一用到字符串sql就报错
        listRest=yield from conn._exeCute(sql)
        count=yield from listRest.fetchall()
        count=len(count)
        resp = cResp()
        global logUserId
        logUserId=''
        for x in users:
            data = cData()
            logUserId=x['accountId']
            data.accountId = x['accountId']
            data.realName=x['realName']
            data.address=json.loads(x['address'])
            data.phone = x['phone']
            data.coin = "%.2f" % round(x['coin'] / 100, 2)
            data.guessCoin = "%.2f" % round(x['guessCoin'] / 100, 2)
            # todo 188 平博调接口拉数据
            pingbo_info=yield from get_pingbo_player_info(x['accountId'])
            data.pinboCoin = pingbo_info['availableBalance']
            data.coin188 = "%.2f" % round(0 / 100, 2)
            data.regTime = x['regTime']
            data.email = x['email']
            data.loginTime = x['loginTime']
            ip_info=yield from getAddressByIp(x['loginIp'])
            data.loginIp = [x['loginIp'],x['loginAddress'],ip_info]
            data.logoutTime = x['logoutTime']
            data.level = x['level']
            data.lastPBCRefreshTime=x['lastPBCRefreshTime']
            data.status = [x['status'], '' if x['lockEndTime'] is None else x['lockEndTime'],'' if x['lockReason'] is None else x['lockReason']]
            data.bankcard = ast.literal_eval(x['bankcard'])
            data.loginDeviceUdid=x['loginDeviceUdid']
            resp.data.append(data)

        resp.count = count
        resp.ret = errorLogic.success[0]
        if pn==1:
            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "查询用户信息",
                'actionTime': getNow(),
                'actionMethod': methodName,
                'actionDetail': "查询用户:{} 信息".format(logUserId),
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))

        # 操作用户日志
        conect = classSqlBaseMgr.getInstance()
        with (yield from classSqlBaseMgr.getInstance(instanceName='probet_oss').objDbMysqlMgr) as conn:
            sql = select([tb_dj_admin_action_bill]).where(
                tb_dj_admin_action_bill.c.actionDetail.like('%' + userId + '%'))
            ret = yield from conn.execute(sql)
            listRes = yield from ret.fetchall()
            for log in listRes:
                logData = UserLogData()
                logData.time = log['actionTime']
                logData.adminAccount = log['accountId']
                logData.detail = log['actionDetail']
                roleNameSql = "select role_name from dj_admin_role WHERE id=(SELECT role_id from dj_admin_account WHERE accountId='{}')".format(
                    log['accountId'])
                roleNameRet = yield from conect._exeCute(roleNameSql)
                roleName = yield from roleNameRet.fetchone()
                logData.roleName = "该管理员不在系统中" if roleName is None else roleName[0]
                resp.logData.append(logData)

        return classJsonDump.dumps(resp)
    except exceptionLogic as e:
        logging.exception(e)
        raise e
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)


