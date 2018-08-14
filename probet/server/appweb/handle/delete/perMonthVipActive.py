import asyncio
from config import vipConfig
from lib.timehelp import timeHelp
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib.jsonhelp import classJsonDump
from lib import certifytoken

class cData():
    def __init__(self):
        self.recharge=0     #当前充值
        self.accountId=''  #账号
        self.validWater=0  #有效流水
        self.activeTime=0  #活动激活时间
        self.level=0       #VIP等级
        self.upLevelWater=0  #升级需要流水
        self.keepLevelWater=0 #保级需要流水
        self.rebate=0 #流水倍数

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""

@asyncio.coroutine
def handleHttp(dictParam: dict):
    #每月VIP活动
    objResp = cResp()
    strAccountId = dictParam.get('accountId','')
    strToken = dictParam.get('token','')

    certifytoken.certify_token(strAccountId, strToken)
    objPlayerData=yield from classDataBaseMgr.getInstance().getPlayerData(strAccountId)
    objActiveData=yield from classDataBaseMgr.getInstance().getActiveData(strAccountId)
    if objPlayerData is None:
        raise exceptionLogic(errorLogic.player_data_not_found)
    if objActiveData is None:
        raise exceptionLogic(errorLogic.active_not_find)
    #判断活动是否完成
    objActiveItme=objActiveData.dictActiveItem.get(2001)
    if objActiveItme is None:
        raise exceptionLogic(errorLogic.active_not_find)
    if objActiveItme.iActiveState==1:
        raise exceptionLogic(errorLogic.active_have_already_get)

    #升级需要的流水
    upWater=vipConfig.vip_config[objPlayerData.iLevel].get('upGradeValidWater')
    #保级需要的流水
    keepWater =vipConfig.vip_config[objPlayerData.iLevel].get('keepValidWater')
    #这个月24小时内充值存款
    payMonthly, orderTime = yield from classSqlBaseMgr.getInstance().getAccountFirstPayByDay(strAccountId)
    # 获取当月有效流水自己平台
    validWater = yield from classSqlBaseMgr.getInstance().getValidWaterMonthly(strAccountId)
    #获取平博当月有效流水
    pingboValidWater=yield from classSqlBaseMgr.getInstance().getAccountPinboHistoryValidWater(timeHelp.monthStartTimestamp(), timeHelp.nextMonthStartTimestamp(),strAccountId)
    pingboValidWater=0 if pingboValidWater.get('validWaterCoin') is None else pingboValidWater.get('validWaterCoin')
    data=cData()
    data.accountId=strAccountId
    #升级还需要的流水
    data.upLevelWater="%.2f"%round((upWater-objPlayerData.iLevelValidWater)/100,2)
    data.keepLevelWater="%.2f"%round((keepWater-(validWater+pingboValidWater))/100,2)
    data.level=objPlayerData.iLevel
    data.rebate=vipConfig.vip_config[objPlayerData.iLevel].get('rebate')
    data.recharge="%.2f"%round(payMonthly/100,2)
    data.activeTime=objActiveData.dictActiveItem.get(2001).iActiveTime
    data.validWater="%.2f"%round((pingboValidWater+validWater)/100,2)
    data.activeId=2001
    objResp.data=data
    return classJsonDump.dumps(objResp)