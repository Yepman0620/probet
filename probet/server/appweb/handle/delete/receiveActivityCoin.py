import asyncio

from datetime import datetime
from logic.enum.enumCoinOp import CoinOp
from config import vipConfig,activeConfig
from datawrapper.playerDataOpWrapper import addPlayerBill
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib.jsonhelp import classJsonDump
from lib import certifytoken
from lib.timehelp.timeHelp import getNow


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""

@asyncio.coroutine
def handleHttp(dictParam: dict):
    #领取活动奖金
    objResp = cResp()
    strAccountId = dictParam.get('accountId','')
    strToken = dictParam.get('token','')
    iActiveId=int(dictParam.get('activeId',0))

    certifytoken.certify_token(strAccountId, strToken)
    objPlayerData,objPlayerLock=yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
    if objPlayerData is None:
        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerLock)
        raise exceptionLogic(errorLogic.player_data_not_found)
    objActiveData, objLock = yield from classDataBaseMgr.getInstance().getActiveDataByLock(strAccountId, None)
    #判断活动是否完成
    objActiveItme=objActiveData.dictActiveItem.get(iActiveId)
    if objActiveItme is None:
        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerLock)
        yield from classDataBaseMgr.getInstance().setActiveDataByLock(objActiveData, objLock)
        raise exceptionLogic(errorLogic.active_not_find)
    if objActiveItme.iActiveState==1:
        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerLock)
        yield from classDataBaseMgr.getInstance().setActiveDataByLock(objActiveData, objLock)

        raise exceptionLogic(errorLogic.active_have_already_get)

    global awardCoin,transFrom
    awardCoin=0
    transFrom=""
    if iActiveId==1000:
        #首冲活动领取
        #计算他该领取的金钱
        recharge=yield from classSqlBaseMgr.getInstance().getFirstRechCoin(strAccountId,objActiveItme.iActiveTime)
        recharge=recharge/100
        config_keys=[]
        for x in activeConfig.activeConfig_cfg.keys():
            if x.startswith('10'):
                config_keys.append(int(x))
        config_keys.sort()
        for x in config_keys:
            if recharge>=int(activeConfig.activeConfig_cfg[str(x)].get('taskConditionParam2')):
                awardCoin=activeConfig.activeConfig_cfg[str(x)].get('awardNum')
                transFrom=activeConfig.activeConfig_cfg[str(x)].get('taskDes')
                continue
            else:
                break
    elif iActiveId==2001:
        #vip月首冲活动
        if objPlayerData.iLevel == 0:
            yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerLock)
            raise exceptionLogic(errorLogic.active_requirements_not_met)
        #1.判断是否领取时间过期
        nowDtObj=datetime.fromtimestamp(getNow())
        actDtobj=datetime.fromtimestamp(objActiveItme.iActiveTime)
        if (nowDtObj.year!=actDtobj.year) and (nowDtObj.month!=actDtobj.month):
            objActiveItme.iActiveState=1
            yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData,objPlayerLock)
            yield from classDataBaseMgr.getInstance().setActiveDataByLock(objActiveData,objLock)
            raise exceptionLogic(errorLogic.active_award_not_get)
        totalCoin,fistrtTime=yield from classSqlBaseMgr.getInstance().getAccountFirstPayByDay(strAccountId)
        totalCoin=0 if totalCoin is None else totalCoin/100
        if totalCoin<10000:
            yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerLock)
            yield from classDataBaseMgr.getInstance().setActiveDataByLock(objActiveData, objLock)
            raise exceptionLogic(errorLogic.active_requirements_not_met)
        for x in activeConfig.activeConfig_cfg.keys():
            if objPlayerData.iLevel == int(activeConfig.activeConfig_cfg[x].get('taskConditionParam2')):
                awardCoin = activeConfig.activeConfig_cfg[x].get('awardNum')
                transFrom = activeConfig.activeConfig_cfg[str(x)].get('taskDes')
    #加钱
    awardCoin=awardCoin*100
    objActiveItme.iActiveState = 1
    objPlayerData.iCoin+=awardCoin
    # 增加不可提现额度
    objActiveData.iNotDrawingCoin+=awardCoin
    #记录流水
    yield from addPlayerBill(strAccountId,awardCoin,CoinOp.coinOpActiveAward,1,transFrom,strAccountId,dictParam.get('srcIp'))
    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerLock)
    yield from classDataBaseMgr.getInstance().setActiveDataByLock(objActiveData, objLock)
    return classJsonDump.dumps(objResp)