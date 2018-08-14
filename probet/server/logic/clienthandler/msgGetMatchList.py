from ssprotocol.dataHeaderDefine import classSSHead
from datawrapper.dataBaseMgr import classDataBaseMgr
from csprotocol.protoMatch import enumGetMatchType
from error.errorCode import exceptionLogic,errorLogic
from csprotocol.protoMatch import protoGetMatchListResp,protoMatchItem
from datawrapper.sqlBaseMgr import classSqlBaseMgr
import asyncio


@asyncio.coroutine
def handleGetMatchList(objHead:classSSHead,objFbReq:dict):

    iGetType = objFbReq.get("iGetType")
    objResp = protoGetMatchListResp()

    listTodayMatchIds = yield from classSqlBaseMgr.getInstance().getTodayMatchIds()
    if iGetType == enumGetMatchType.getTypeAll:
        listMatchIds = yield from classSqlBaseMgr.getInstance().getAllMatchIds()
        listMatchDatas = yield from classDataBaseMgr.getInstance().getMatchDataList(listMatchIds)
    elif iGetType == enumGetMatchType.getTypeToday:
        listMatchDatas = yield from classDataBaseMgr.getInstance().getMatchDataList(listTodayMatchIds)
    elif iGetType == enumGetMatchType.getTypeLive:
        listMatchIds = yield from classSqlBaseMgr.getInstance().getLiveMatchData()
        listMatchDatas = yield from classDataBaseMgr.getInstance().getMatchDataList(listMatchIds)
    elif iGetType == enumGetMatchType.getTypeNotStart:
        listMatchIds = yield from classSqlBaseMgr.getInstance().getNotBeginMatchIds()
        listMatchDatas = yield from classDataBaseMgr.getInstance().getMatchDataList(listMatchIds)
    else:
        raise exceptionLogic(errorLogic.client_param_invalid)


    retList = yield from classSqlBaseMgr.getInstance().getMatchStateCount()
    #计算一下数量
    iNotBeginNum = 0
    iLiveNum = 0
    iResultNum = 0
    for varItem in retList:
        if varItem["matchState"] == 0:
            #早盘
            iNotBeginNum += varItem['count']
        elif varItem["matchState"] == 1 or varItem["matchState"] == 2:
            #live
            iLiveNum += varItem['count']
        else:
            iResultNum += varItem['count']
    iTodayNum = len(listTodayMatchIds)
    objResp.listStateCountList = [iLiveNum+iNotBeginNum,iTodayNum,iLiveNum,iNotBeginNum]

    #objResp.listStateCountList = retList
    #统一一批拿出guess数据
    listGuessIds = []
    for var_matchData in listMatchDatas:
        listGuessIds.extend(var_matchData.arrayGuess)

    dictGuessDatas = yield from classDataBaseMgr.getInstance().getGuessDataListRetDict(listGuessIds)

    for var_matchData in listMatchDatas:
        objMatchItem = protoMatchItem(var_matchData)
        for var_round,var_list in var_matchData.dictGuess.items():
            for var_guess_id in var_list:
                objGuessData = dictGuessDatas.get(var_guess_id)
                if objGuessData is not None:
                    objMatchItem.buildRoundGuess(var_round,objGuessData)
        objResp.listMatchList.append(objMatchItem)

    return objResp
