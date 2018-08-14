import asyncio
from error.errorCode import errorLogic,exceptionLogic
from ssprotocol import dataHeaderDefine
from datawrapper.dataBaseMgr import classDataBaseMgr
from ssprotocol.protoDataCenterResult import result_msgId,AwardReq
from lib.timehelp import timeHelp
from lib.pubSub.pubMgr import classPubMgr

@asyncio.coroutine
def handleHttp(dict_param:dict):

    strMatchId = dict_param["strMatchId"]
    iAwardNum = int(dict_param['iAwardNum'])
    iAwardType = int(dict_param['iAwardType'])
    iWinOrLose = int(dict_param['iWinOrLose'])


    objMatchData, objMatchDataLock = yield from classDataBaseMgr.getInstance().getMatchDataByLock(strMatchId)
    if objMatchData is None:
        # TODO release lock
        raise exceptionLogic(errorLogic.guess_data_not_found)

    objMatchData.iAwardFlag = 1
    objMatchData.iAwardType = iAwardType
    objMatchData.iAwardNum = iAwardNum
    objMatchData.iWinOrLose = iWinOrLose

    yield from classDataBaseMgr.getInstance().setMatchDataByLock(objMatchData, objMatchDataLock)

    #加入赠送列表
    yield from classDataBaseMgr.getInstance().delMatchCancelAwardedList(objMatchData.strMatchId, timeHelp.getNow())
    yield from classDataBaseMgr.getInstance().addMatchAwardedList(objMatchData.strMatchId, timeHelp.getNow())

    #全部奖励
    msgHead = dataHeaderDefine.classResultHead()
    msgHead.strMsgId = result_msgId.msg_award
    msgBody = AwardReq()
    msgBody.strMatchId = strMatchId
    msgBody.iWinOrLose = iWinOrLose
    msgBody.iAwardNum = iAwardNum
    msgBody.iAwardType = iAwardType

    yield from classPubMgr.getInstance("resultPub").publish(msgHead, msgBody)
