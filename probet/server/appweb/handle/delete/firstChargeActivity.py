import asyncio

from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib.jsonhelp import classJsonDump
from lib import certifytoken

class cData():
    def __init__(self):
        self.validWater=0  #有效流水
        self.recharge=0 #当前充值
        self.activeTime=0  #活动激活时间

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""

@asyncio.coroutine
def handleHttp(dictParam: dict):
    #首充活动
    objResp = cResp()
    strAccountId = dictParam.get('accountId','')
    strToken = dictParam.get('token','')

    certifytoken.certify_token(strAccountId, strToken)
    objActiveData=yield from classDataBaseMgr.getInstance().getActiveData(strAccountId)
    if objActiveData is None:
        raise exceptionLogic(errorLogic.active_not_find)
    #判断活动是否完成
    objActiveItme=objActiveData.dictActiveItem.get(1000)
    if objActiveItme is None:
        raise exceptionLogic(errorLogic.active_not_find)
    if objActiveItme.iActiveState==1:
        raise exceptionLogic(errorLogic.active_have_already_get)

    activeTime=objActiveData.dictActiveItem.get(1000).iActiveTime
    recharge=yield from classSqlBaseMgr.getInstance().getFirstRechCoin(strAccountId,activeTime)
    #获取当月有效流水自己平台
    validWater=yield from classSqlBaseMgr.getInstance().getValidWaterMonthly(strAccountId)
    pingboValidWater=yield from classSqlBaseMgr.getInstance().getAccountPinboHistoryValidWater(activeTime,activeTime+86400,strAccountId)
    pingboValidWater=0 if pingboValidWater.get('validWaterCoin') is None else pingboValidWater.get('validWaterCoin')
    data=cData()
    data.recharge="%.2f"%round(recharge/100,2)
    data.validWater="%.2f"%round((validWater+pingboValidWater)/100,2)
    data.activeTime=objActiveData.dictActiveItem.get(1000).iActiveTime
    data.activeId=1000
    objResp.data=data
    return classJsonDump.dumps(objResp)