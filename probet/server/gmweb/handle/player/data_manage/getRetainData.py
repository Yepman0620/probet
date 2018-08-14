import asyncio
import json
import logging
from datetime import datetime
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.tools import token_required, permission_required
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow
from logic.logicmgr.checkParamValid import checkIsInt

class cData():
    def __init__(self):
        self.time=0
        self.regCount=0
        self.retainRate=[]
        self.day60='0.00%'
        self.day90='0.00%'

class cResp():
    def __init__(self):
        self.ret = 0
        self.count = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('留存分析')
@asyncio.coroutine
def handleHttp(request: dict):
    """根据时间，渠道获取留存数据"""
    channel = request.get('channel', '')
    startTime = request.get('startTime', 0)
    endTime = request.get('endTime', 0)
    objRep = cResp()
    #TODO Warning: Truncated incorrect DOUBLE value: 'test1'
    if not all([startTime,endTime]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    if (not checkIsInt(startTime)) or (not checkIsInt(endTime)):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        conn=classSqlBaseMgr.getInstance(instanceName='probet_oss')
        endTime=endTime+24*3600
        days=(endTime-startTime)/(24*3600)
        days=int(days)
        # 获取登录时间 留存：次日登录账号（在注册的账号中的）/当日注册的账号
        for x in range(days):
            data=cData()
            #1.获取startTime注册账号量及accountId
            if channel:
                sql = "select accountId from dj_regbill WHERE dj_regbill.agentId='{}' AND dj_regbill.regTime BETWEEN {} AND {} ".format(channel,
                                                                            startTime + x * 24 * 3600,startTime + (x+1) * 24 * 3600)
            else:
                sql="select accountId from dj_regbill WHERE dj_regbill.regTime BETWEEN {} AND {} ".format(startTime+x*24*3600,
                                                                    startTime+(x+1)*24*3600)

            listRest=yield from conn._exeCute(sql)
            idList=yield from listRest.fetchall()
            if len(idList)==0:
                data.time=startTime+x*24*3600
            else:
                ids = []
                for a in idList:
                    ids.append(a[0])
                if len(ids)==1:
                    ids=str(tuple(ids)).replace(r',','')
                else:
                    ids=tuple(ids)
                #注册量
                reg_count=len(idList)
                data.regCount=reg_count
                data.time=startTime+x*24*3600
                # todo 60天后留存   90天后留存
                day60_sql = "select count(DISTINCT(accountId)) from dj_loginbill WHERE dj_loginbill.accountId in {} AND dj_loginbill.loginTime BETWEEN {} AND {} ".format(ids,
                    startTime + 60 * 24 * 3600, startTime + 61 * 24 * 3600)
                day90_sql = "select count(DISTINCT(accountId)) from dj_loginbill WHERE dj_loginbill.accountId in {} AND dj_loginbill.loginTime BETWEEN {} AND {} ".format(
                    ids,startTime + 90 * 24 * 3600, startTime + 91 * 24 * 3600)
                day60Ret=yield from conn._exeCute(day60_sql)
                day60Res=yield from day60Ret.fetchone()
                data.day60="%.2f"%round((day60Res[0]/reg_count)*100,2)+'%'
                day90Ret = yield from conn._exeCute(day90_sql)
                day90Res = yield from day90Ret.fetchone()
                data.day90 = "%.2f" % round((day90Res[0] / reg_count) * 100, 2) + '%'

                loop_count=1
                loop_befor_count=0
                dtObj=datetime.fromtimestamp(startTime)
                month=dtObj.month
                while True:
                    timeStamp=startTime-loop_befor_count*24*3600
                    loop_now_month = datetime.fromtimestamp(timeStamp).month
                    if loop_now_month!=month:
                        break
                    data.retainRate.insert(0,[startTime - loop_befor_count * 24 * 3600,
                                            "%.2f" % round(0, 2) + '%'])
                    loop_befor_count+=1
                while True:
                    timeStamp=startTime+loop_count*24*3600
                    loop_now_month=datetime.fromtimestamp(timeStamp).month
                    if loop_now_month!=month:
                        #不是本月
                        break
                    else:
                        #是本月
                        sql="select count(DISTINCT(accountId)) from dj_loginbill WHERE dj_loginbill.accountId in {} AND dj_loginbill.loginTime BETWEEN {} AND {} ".format(ids,
                                                                                                          startTime+loop_count*24*3600,startTime+(loop_count+1)*24*3600)
                        listRest=yield from conn._exeCute(sql)
                        login_count=yield from listRest.fetchone()
                        data.retainRate.append([startTime+loop_count*24*3600,"%.2f"%round((login_count[0]/reg_count)*100,2)+'%'])
                        loop_count+=1

            objRep.data.append(data)
        objRep.count=days
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "查询留存信息",
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionDetail': "查询:{} 留存信息".format(channel),
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)
