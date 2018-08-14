import asyncio
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from logic.logicmgr.checkParamValid import checkIsInt

class cData():
    def __init__(self):
        self.date=0             #日期
        self.channelId=0        #渠道Id
        self.channel=''         #渠道
        self.platform=0         #平台
        self.dailyNew=0         #每日新增
        self.totalReg=0         #总注册
        self.DAU=0              #DAU
        self.dailyRecharge=0    #每日充值
        self.RechargeCount=0    #充值人数
        self.dayRegHisRecharge=0#当日注册用户历史总充值
        self.LTV='0.00'         #LTV   当日注册用户历史总充值/当日新增

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('权限管理')
@asyncio.coroutine
def handleHttp(request: dict):
    """获取渠道LTV数据"""
    channel = request.get('channel', '')
    startTime = request.get('startTime', 0)
    endTime = request.get('endTime', 0)

    objRep = cResp()

    if not all([startTime,endTime]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    if (not checkIsInt(startTime)) or (not checkIsInt(endTime)):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        # conn=classSqlBaseMgr.getInstance(instanceName='probet_oss')
        with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
            over_all_data=cData()
            #todo
        return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)
