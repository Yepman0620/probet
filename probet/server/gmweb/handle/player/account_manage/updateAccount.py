import asyncio
import json
from gmweb.handle.pinbo.update_player_status import update_status
from logic.regex import precompile
from sqlalchemy import select
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.timehelp import timeHelp
from lib.timehelp.timeHelp import getNow
from lib.pwdencrypt import PwdEncrypt
from osssvr.utils.models import tb_dj_admin_action_bill
import logging


class cData():
    def __init__(self):
        self.phone = ""

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
@permission_required('基本信息管理')
@asyncio.coroutine
def handleHttp(request: dict):
    userId = request.get('userId', '')
    password = request.get('password', '')
    transPwd=request.get('transPwd','')
    phone = request.get('phone', '')
    email = request.get('email', '')
    lockTime = request.get('lockTime', '')
    lockReason = request.get('lockReason', '')
    status = request.get('status', '')
    level = request.get('level', '')
    realName=request.get('realName','')

    if not userId:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(userId)
        if objPlayerData is None:
            logging.debug(errorLogic.player_data_not_found)
            raise exceptionLogic(errorLogic.player_data_not_found)
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "修改用户信息",
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionIp': request.get('srcIp', ''),
        }

        if password:
            # 修改密码
            pwd_md5 = PwdEncrypt().create_md5(password)
            objPlayerData.strPassword = pwd_md5
            dictActionBill['actionDetail']= "修改用户：{} 的登录密码".format(userId)
        elif phone:
            objPlayerData.strPhone = phone
            dictActionBill['actionDetail'] = "修改用户：{} 的电话号码为：{}".format(userId,phone)
        elif email:
            objPlayerData.strEmail = email
            dictActionBill['actionDetail'] = "修改用户：{} 的邮箱为：{}".format(userId, email)
        elif level:
            objPlayerData.iLevel = level
            dictActionBill['actionDetail'] = "修改用户：{} 的等级为：{}".format(userId, level)
        elif transPwd:
            #修改交易密码
            if precompile.TradePassword.search(transPwd) is None:
                raise exceptionLogic(errorLogic.player_TradePwd_length_out_of_range)
            strTradePwd = PwdEncrypt().create_md5(transPwd)
            objPlayerData.strTradePassword=strTradePwd
            dictActionBill['actionDetail'] = "修改用户：{} 的交易密码".format(userId)
        elif realName:
            objPlayerData.strRealName = realName
            dictActionBill['actionDetail'] = "修改用户：{} 的姓名为：{}".format(userId, realName)
        else:
            if status == 0:
                # 解封
                objPlayerData.iStatus = status
                objPlayerData.iLockStartTime = 0
                objPlayerData.iLockEndTime = 0
                objPlayerData.strLockReason = ""
                # yield from update_status(userId,'ACTIVE')

            else:
                # 冻结账号
                if not all([lockTime, lockReason]):
                    logging.debug(errorLogic.lockTime_or_lockReason_lack)
                    raise exceptionLogic(errorLogic.lockTime_or_lockReason_lack)
                objPlayerData.iStatus = 1
                objPlayerData.iLockStartTime=timeHelp.getNow()
                objPlayerData.iLockEndTime = timeHelp.getNow() + int(lockTime)
                objPlayerData.strLockReason = lockReason
                # yield from update_status(userId,'SUSPENDED')
            dictActionBill['actionDetail'] = "为用户：{} 解封账号" if status==0 else "冻结用户：{} 账号，冻结原因：{}".format(userId,lockReason)

        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        resp = cResp()

        data = cData()
        data.realName=objPlayerData.strRealName
        data.accountId = objPlayerData.strAccountId
        data.phone = objPlayerData.strPhone
        data.coin = "%.2f" % round(objPlayerData.iCoin / 100, 2)
        data.guessCoin = "%.2f" % round(objPlayerData.iGuessCoin / 100, 2)
        data.pinboCoin = "%.2f" % round(objPlayerData.iPingboCoin / 100, 2)
        #todo 188
        data.coin188 = "%.2f" % round(0 / 100, 2)
        data.regTime = objPlayerData.iRegTime
        data.email = objPlayerData.strEmail
        data.loginTime = objPlayerData.iLastLoginTime
        data.loginIp = [objPlayerData.strLastLoginUdid, objPlayerData.strLoginAdderss]
        data.logoutTime = objPlayerData.iLogoutTime
        data.level = objPlayerData.iLevel
        data.status = [objPlayerData.iStatus, objPlayerData.iLockEndTime, objPlayerData.strLockReason]
        data.bankcard = objPlayerData.arrayBankCard
        resp.data.append(data)

        # 操作用户日志
        conect=classSqlBaseMgr.getInstance()
        with (yield from classSqlBaseMgr.getInstance(instanceName='probet_oss').objDbMysqlMgr) as conn:
            sql = select([tb_dj_admin_action_bill]).where(tb_dj_admin_action_bill.c.actionDetail.like('%' + userId + '%'))
            ret=yield from conn.execute(sql)
            listRes=yield from ret.fetchall()
            for log in listRes:
                logData=UserLogData()
                logData.time=log['actionTime']
                logData.adminAccount=log['accountId']
                logData.detail=log['actionDetail']
                roleNameSql="select role_name from dj_admin_role WHERE id=(SELECT role_id from dj_admin_account WHERE accountId='{}')".format(log['accountId'])
                roleNameRet=yield from conect._exeCute(roleNameSql)
                roleName=yield from roleNameRet.fetchone()
                logData.roleName="该管理员不在系统中" if roleName is None else roleName[0]
                resp.logData.append(logData)
        return classJsonDump.dumps(resp)
    except exceptionLogic as e:
        logging.error(repr(e))
        raise e

