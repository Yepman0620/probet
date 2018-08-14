import asyncio

from error.errorCode import errorLogic,exceptionLogic

from ssprotocol import dataHeaderDefine
from datawrapper.dataBaseMgr import classDataBaseMgr
from ssprotocol.protoDataCenterResult import result_msgId,CancelAwardReq

@asyncio.coroutine
def handleHttp(dict_param:dict):

    strMatchId = dict_param["strMatchId"]

    objMatchData, objMatchDataLock = yield from classDataBaseMgr.getInstance().getMatchDataByLock(strMatchId)
    if objMatchData is None:
        # TODO release lock
        raise exceptionLogic(errorLogic.guess_data_not_found)

    objMatchData.iAwardFlag = 1
    yield from classDataBaseMgr.getInstance().setMatchDataByLock(objMatchData, objMatchDataLock)

    yield from classDataBaseMgr.getInstance().delMatchAwardedList(objMatchData.strMatchId)
    yield from classDataBaseMgr.getInstance().addMatchCancelAwardedList(objMatchData.strMatchId)

    #全部奖励
    msgHead = dataHeaderDefine.classResultHead()
    msgHead.strMsgId = result_msgId.msg_cancel_award
    msgBody = CancelAwardReq()
    msgBody.strMatchId = strMatchId
    #msgBody.strGuessId = strGuessId
    #msgBody.strDictKey = var_key
    msgBody.iWinOrLose = objMatchData.iWinOrLose
    msgBody.iCancelCoin = objMatchData.iAwardFlag
    msgBody.iCancelNum = objMatchData.iAwardNum
    yield from classPubMgr.getInstance("resultPub").publish(msgHead, msgBody)


