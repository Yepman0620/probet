import asyncio
from lib.timehelp import timeHelp
from error.errorCode import errorLogic,exceptionLogic
from lib.pubSub.pubMgr import classPubMgr
from ssprotocol import dataHeaderDefine
from datawrapper.dataBaseMgr import classDataBaseMgr
from ssprotocol.protoDataCenterResult import result_msgId,ResultReq
from datawrapper.pushDataOpWrapper import broadCastGuessData

@asyncio.coroutine
def handleHttp(dict_param:dict):

    strMatchId = dict_param["strMatchId"]
    strGuessId = dict_param['strGuessId']
    strWinKey = dict_param['strWinKey']

    objGuessData, objGuessDataLock = yield from classDataBaseMgr.getInstance().getGuessDataByLock(strGuessId)
    if objGuessData is None:
        #TODO release lock
        raise exceptionLogic(errorLogic.guess_data_not_found)

    if strWinKey not in objGuessData.dictCTR:
        #TODO release lock
        raise exceptionLogic(errorLogic.guess_result_key_not_found)

    objGuessData.iGuessState = 4
    objGuessData.strGuessResult = strWinKey

    yield from classDataBaseMgr.getInstance().setGuessDataByLock(objGuessData,objGuessDataLock)

    yield from broadCastGuessData([objGuessData], "broadCastPub")

    for var_key in objGuessData.dictCTR.keys():
        msgHead = dataHeaderDefine.classResultHead()
        msgHead.strMsgId = result_msgId.msg_result if len(strWinKey) else result_msgId.msg_no_result
        msgBody = ResultReq()
        msgBody.strMatchId = strMatchId
        msgBody.strGuessId = strGuessId

        msgBody.strDictKey = var_key
        if var_key == strWinKey:
            msgBody.iWinOrLose = 1
        else:
            msgBody.iWinOrLose = 0

        yield from classPubMgr.getInstance("resultPub").publish(msgHead, msgBody)

    #判断比赛是否已经全部发奖
    objMatchData, objMatchDataLock = yield from classDataBaseMgr.getInstance().getMatchDataByLock(strMatchId)
    if objMatchData is None:
        # TODO release lock
        raise exceptionLogic(errorLogic.match_data_not_found)

    if strGuessId not in objMatchData.arrayAwardGuess:
        objMatchData.arrayAwardGuess.append(strGuessId)

    yield from classDataBaseMgr.getInstance().setMatchDataByLock(objMatchData,objMatchDataLock)
    if len(objMatchData.arrayAwardGuess) == len(objMatchData.arrayGuess):
        yield from classDataBaseMgr.getInstance().setMatchResultFinish(strMatchId,objMatchData.strMatchType,timeHelp.getNow())
