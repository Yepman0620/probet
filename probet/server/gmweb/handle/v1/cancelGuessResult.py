import asyncio
from error.errorCode import errorLogic,exceptionLogic
from lib.pubSub.pubMgr import classPubMgr
from ssprotocol import dataHeaderDefine
from datawrapper.dataBaseMgr import classDataBaseMgr
from ssprotocol.protoDataCenterResult import result_msgId,CancelAwardReq

@asyncio.coroutine
def handleHttp(dict_param:dict):

    strMatchId = dict_param["strMatchId"]


    iBeginTime = dict_param['iBeginTime']
    iEndTime = dict_param['iEndTime']

    objMatchData, objMatchDataLock = yield from classDataBaseMgr.getInstance().getMatchDataByLock(strMatchId)
    if objMatchData is None:
        raise exceptionLogic(errorLogic.match_data_not_found)
    else:
        for var_guess_id in objMatchData.arrayGuess:
            objMatchData.arrayCancelResultGuessId.append(var_guess_id)

        objMatchData.iCancelResultFlag = 1
        objMatchData.iCancelResultBeginTime = iBeginTime
        objMatchData.iCancelResultEndTime = iEndTime

        yield from classDataBaseMgr.getInstance().setMatchDataByLock(objMatchData,objMatchDataLock)

        for var_guess_id in objMatchData.arrayGuess:
            yield from cancelGuessResult(strMatchId, var_guess_id, "", iBeginTime, iEndTime)


@asyncio.coroutine
def cancelGuessResult(strMatchId,strGuessId,strChooseId,iBeginTime,iEndTime):
    objGuessData, objGuessDataLock = yield from classDataBaseMgr.getInstance().getGuessDataByLock(strGuessId)
    if objGuessData is None:
        # TODO release lock
        raise exceptionLogic(errorLogic.guess_data_not_found)

    yield from classDataBaseMgr.getInstance().setGuessDataByLock(objGuessData, objGuessDataLock)

    if len(strChooseId) <= 0:
        # 全部无效
        for var_key, var_value in objGuessData.dictCTR.items():
            yield from classDataBaseMgr.getInstance().resetResultRedisListByScore(strGuessId, var_value.strId,
                                                                                   iBeginTime)

        for var_key in objGuessData.dictCTR.keys():
            msgHead = dataHeaderDefine.classResultHead()
            msgHead.strMsgId = result_msgId.msg_cancel_result
            msgBody = CancelAwardReq()
            msgBody.strMatchId = strMatchId
            msgBody.strGuessId = strGuessId
            msgBody.strDictKey = var_key
            msgBody.iBeginTime = iBeginTime
            msgBody.iEndTime = iEndTime

            yield from classPubMgr.getInstance("resultPub").publish(msgHead, msgBody)

    else:
        if strChooseId in objGuessData.dictCTR:
            yield from classDataBaseMgr.getInstance().resetResultRedisListByScore(strGuessId, strChooseId, iBeginTime)

            msgHead = dataHeaderDefine.classResultHead()
            msgHead.strMsgId = result_msgId.msg_cancel_result
            msgBody = CancelAwardReq()
            msgBody.strMatchId = strMatchId
            msgBody.strGuessId = strGuessId
            msgBody.strDictKey = strChooseId
            msgBody.iBeginTime = iBeginTime
            msgBody.iEndTime = iEndTime

            yield from classPubMgr.getInstance("resultPub").publish(msgHead, msgBody)