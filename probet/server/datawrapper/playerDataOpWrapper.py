import asyncio
import json

import logging

from logic.data.userData import classUserData,classUserCoinHistory,classAgentCommissionData
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import errorLogic,exceptionLogic,exceptionLogic
from logic.logicmgr import orderGeneral
from lib.timehelp import timeHelp
"""
from csprotocol.protoPlayer import protoPushPlayerCoin
from csprotocol.protocol import pushPlayerCoin
from lib.onlineMgr import classOnlineMgr
from lib.pushMgr import classPushMgr
from ssprotocol.dataHeaderDefine import classSSHead
"""

@asyncio.coroutine
def opPlayerCoinByAccountId(accountId:str,addCoin:int,reenTrantLock:str=None):
    objPlayerData,objPlayerLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(accountId,reenTrantLock)
    if objPlayerData is None:
        raise exceptionLogic(errorLogic.player_data_not_found)

    objPlayerData.iCoin += addCoin

@asyncio.coroutine
def opPlayerCoinByAccountIdReleaseLock(accountId:str,addCoin:int,reenTrantLock:str=None):
    objPlayerData,objPlayerLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(accountId,reenTrantLock)
    if objPlayerData is None:
        raise exceptionLogic(errorLogic.player_data_not_found)

    objPlayerData.iCoin += addCoin
    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerLock)


@asyncio.coroutine
def opPlayerCoinByPlayerData(objPlayerData:classUserData,objPlayerLock:str,addCoin:int,addType:int):

    if objPlayerData is None:
        #把锁还回去
        #yield from classDataBaseMgr.getInstance().releasePlayerDataLock(objPlayerData.strAccount,objPlayerLock)
        raise exceptionLogic(errorLogic.player_data_not_found)

    objPlayerData.iCoin += addCoin


@asyncio.coroutine
def opPlayerCoinByPlayerDataReleaseLock(objPlayerData:classUserData,objPlayerLock:str,addCoin:int):

    if objPlayerData is None:
        #把锁还回去
        #yield from classDataBaseMgr.getInstance().releasePlayerDataLock(objPlayerData.strAccount,objPlayerLock)
        raise exceptionLogic(errorLogic.player_data_not_found)

    objPlayerData.iCoin += addCoin
    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData,objPlayerLock)


@asyncio.coroutine
def addPlayerBill(strAccountId,iOpCoin,iBalance,enumOp,tradeState,transFrom="", transTo="",srcIp="",strOrderId="",iValidWater=0,strDes="",):

    objNewBillHis = classUserCoinHistory()
    if len(strOrderId) <= 0:
        objNewBillHis.strOrderId = orderGeneral.generalOrderId()  # 流水单号
    else:
        objNewBillHis.strOrderId = strOrderId
    objNewBillHis.iTime = timeHelp.getNow()  # 发生时间
    objNewBillHis.iCoin = iOpCoin  # 单位 rmb 分
    objNewBillHis.iBalance = iBalance  # 余额
    objNewBillHis.iTradeType = enumOp  # 详见coin的枚举类型  1：存款 2：取款 3：转账
    objNewBillHis.iTradeState = tradeState  # 1：成功 2：等待 4：失败
    objNewBillHis.strAccountId = strAccountId  # 单号归属账号id
    objNewBillHis.strIp = srcIp  # 客户的请求的ip
    objNewBillHis.iEndTime = 0  # 流水结束时间
    objNewBillHis.strTransFrom = transFrom  # 来自哪个钱包
    objNewBillHis.strTransTo = transTo  # 转到哪个钱包,或者转到哪个银行卡（存款 提款的时候用）
    objNewBillHis.strDes = strDes
    objNewBillHis.iValidWater = iValidWater

    yield from classDataBaseMgr.getInstance().addPlayerCoinRecord(strAccountId, objNewBillHis)

    return objNewBillHis


"""
@asyncio.coroutine
def addPlayerCoinByAccountId(accountId:str,addCoin:int):
    iCoin = yield from classDataBaseMgr.getInstance().increasePlayerCoin(accountId,addCoin)

    #推送数据包给客户端
    dictOnlineInfo = yield from classOnlineMgr.getInstance().getOnlineClient(accountId)
    if dictOnlineInfo is not None:
        # 没在线，不用推送了
        objPushSSHead = classSSHead()
        objPushSSHead.strAccountId = accountId
        objPushSSHead.strMsgId = pushPlayerCoin
        objPushSSHead.strClientUdid = dictOnlineInfo['connectUid']

        objResp = protoPushPlayerCoin()
        objResp.strAccountId = accountId
        objResp.iCoin = iCoin


        yield from classPushMgr.getInstance().push(dictOnlineInfo['host'], dictOnlineInfo['groupId'],
                                                   objPushSSHead, objResp)

    return iCoin

@asyncio.coroutine
def decPlayerCoinByAccountId(accountId:str,decCoin:int):
    iCoin = yield from classDataBaseMgr.getInstance().decreasePlayerCoin(accountId, decCoin)
    # 推送数据包给客户端
    dictOnlineInfo = yield from classOnlineMgr.getInstance().getOnlineClient(accountId)
    if dictOnlineInfo is not None:
        # 没在线，不用推送了
        objPushSSHead = classSSHead()
        objPushSSHead.strAccountId = accountId
        objPushSSHead.strMsgId = pushPlayerCoin
        objPushSSHead.strClientUdid = dictOnlineInfo['connectUid']

        objResp = protoPushPlayerCoin()
        objResp.strAccountId = accountId
        objResp.iCoin = iCoin

        yield from classPushMgr.getInstance().push(dictOnlineInfo['host'], dictOnlineInfo['groupId'],
                                                   objPushSSHead, objResp)
    return iCoin
"""



