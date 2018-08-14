import asyncio
import pickle
from ssprotocol.dataHeaderDefine import classSSHead
from csprotocol.protocol import pushMatchList,pushMatchBasicList,pushGuessList
from csprotocol.protoMatch import protoMatchItem,protoGuessItem,protoPushMatchBasicData,protoPushGuessData,protoPushMatchData
from csprotocol.protoGm import protoPushPinboRepireData
from csprotocol.protoMsg import protoPushPlayerMsg
from lib.pubSub.pubMgr import classPubMgr

from csprotocol.protoPlayer import protoPushPlayerCoin,protoPushPlayerCenterCoin
from csprotocol.protocol import pushPlayerCoin,pushPinboRepair,pushPlayerCenterCoin, pushMessage
from lib.onlineMgr import classOnlineMgr
from lib.pushMgr import classPushMgr
from ssprotocol.dataHeaderDefine import classSSHead


@asyncio.coroutine
def broadCastMatchData(matchDataList:list,guessDataDict:dict,pubInsName:str=None):

    objPushSSHead = classSSHead()
    objPushSSHead.iBroadCast = 1
    objPushSSHead.strMsgId = pushMatchList

    objResp = protoPushMatchData()
    for var_match in matchDataList:
        objNewMatchResp = protoMatchItem(var_match)
        for var_round,var_guess_id_list in var_match.dictGuess.item():
            for var_guess_id in var_guess_id_list:
                objGuessData = guessDataDict.get(var_guess_id,None)
                if objGuessData is not None:

                    objNewMatchResp.buildRoundGuess(var_round,objGuessData)
        objResp.listMatchList.append(objNewMatchResp)

    yield from classPubMgr.getInstance(pubInsName).publish(objPushSSHead,objResp)


@asyncio.coroutine
def broadCastMatchBasicData(matchDataList:list,pubInsName:str=None):

    objPushSSHead = classSSHead()
    objPushSSHead.iBroadCast = 1
    objPushSSHead.strMsgId = pushMatchBasicList

    objResp = protoPushMatchBasicData()
    for var_match in matchDataList:
        objNewMatchResp = protoMatchItem(var_match)
        objResp.listMatchBasicList.append(objNewMatchResp)

    yield from classPubMgr.getInstance(pubInsName).publish(objPushSSHead,objResp)

@asyncio.coroutine
def broadCastGuessData(guessDataList:list,pubInsName:str=None):

    objPushSSHead = classSSHead()
    objPushSSHead.iBroadCast = 1
    objPushSSHead.strMsgId = pushGuessList

    objResp = protoPushGuessData()
    for var_guess in guessDataList:
        objNewGuessResp = protoGuessItem(var_guess)
        objResp.listGuessList.append(objNewGuessResp)

    yield from classPubMgr.getInstance(pubInsName).publish(objPushSSHead, objResp)

@asyncio.coroutine
def coroPushPlayerCoin(accountId:str,iCoin):

    dictOnlineInfo = yield from classOnlineMgr.getInstance().getOnlineClient(accountId)
    if dictOnlineInfo is not None:
        # 没在线，不用推送了
        objPushSSHead = classSSHead()
        objPushSSHead.strAccountId = accountId
        objPushSSHead.strMsgId = pushPlayerCoin
        objPushSSHead.strClientUdid = dictOnlineInfo['connectUid']

        objResp = protoPushPlayerCoin()
        objResp.strAccountId = accountId
        objResp.iCoin = "%.2f"%round(iCoin/100,2)

        yield from classPushMgr.getInstance().push(dictOnlineInfo['host'], dictOnlineInfo['groupId'],
                                                   objPushSSHead, objResp)

    return iCoin


@asyncio.coroutine
def pushPlayerMsg(accountId,msgId,pubInsName=None):
    dictOnlineInfo = yield from classOnlineMgr.getInstance().getOnlineClient(accountId)
    if dictOnlineInfo is not None:
        # 没在线，不用推送了
        objPushSSHead = classSSHead()
        objPushSSHead.strAccountId = accountId
        objPushSSHead.strMsgId = pushMessage

        objResp = protoPushPlayerMsg()
        objResp.accountId = accountId
        objResp.msgId = msgId

        yield from classPubMgr.getInstance(pubInsName).publish(objPushSSHead, objResp)


@asyncio.coroutine
def pushPinboRepairData(iEndTime,iRepairFlag,iSurplusTime,iStartTime,pubInsName=None):
    #推送pinbo维护状态信息
    objPushSSHead = classSSHead()
    objPushSSHead.iBroadCast = 1 # 全体
    objPushSSHead.strMsgId = pushPinboRepair

    objResp = protoPushPinboRepireData()
    objResp.end_time = iEndTime
    objResp.repairFlag = iRepairFlag
    objResp.surplus_time = iSurplusTime
    objResp.start_time = iStartTime

    yield from classPubMgr.getInstance(pubInsName).publish(objPushSSHead, objResp)



@asyncio.coroutine
def coroPushPlayerCenterCoin(accountId:str,iCenterCoin,coinKind:str):

    dictOnlineInfo = yield from classOnlineMgr.getInstance().getOnlineClient(accountId)
    if dictOnlineInfo is not None:
        # 没在线，不用推送了
        objPushSSHead = classSSHead()
        objPushSSHead.strAccountId = accountId
        objPushSSHead.strMsgId = pushPlayerCenterCoin
        objPushSSHead.strClientUdid = dictOnlineInfo['connectUid']

        objResp = protoPushPlayerCenterCoin()
        objResp.strAccountId = accountId
        objResp.strCoinKind=coinKind
        objResp.iCenterCoin = "%.2f"%round(iCenterCoin/100,2)

        yield from classPushMgr.getInstance().push(dictOnlineInfo['host'], dictOnlineInfo['groupId'],
                                                   objPushSSHead, objResp)

    return iCenterCoin
