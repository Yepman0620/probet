import asyncio
from error.errorCode import exceptionLogic,errorLogic
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.timehelp import timeHelp

@asyncio.coroutine
def handleHttp(dict_param:dict):
    strMatchId = dict_param["strMatchId"]
    strGuessId = dict_param["strGuessId"]

    objMatchData, objMatchDataLock = yield from classDataBaseMgr.getInstance().getMatchDataByLock(strMatchId)
    if objMatchData != None:

        #记录要删除的场次id array
        iCheckDeleteRound = -1
        if strGuessId in objMatchData.arrayGuess:
            objMatchData.arrayGuess.remove(strGuessId)

        for var_round,var_list_guess in objMatchData.dictGuess.items():
            if strGuessId in var_list_guess:
                var_list_guess.remove(strGuessId)
                iCheckDeleteRound = var_round
                break

        if iCheckDeleteRound != -1:
            if len(objMatchData.dictGuess[iCheckDeleteRound]) <= 0:
                #如果这个对应的round 没有了，则删除这个round的key，免得这个客户端数据为空的值
                objMatchData.dictGuess.pop(iCheckDeleteRound)

        yield from classDataBaseMgr.getInstance().delGuessData(strGuessId)
        yield from classDataBaseMgr.getInstance().setMatchDataByLock(objMatchData,objMatchDataLock)

        #如果删错玩法，也看看是否已经派往完奖励
        if len(objMatchData.arrayAwardGuess) > 0:
            if len(objMatchData.arrayAwardGuess) == len(objMatchData.arrayGuess) and objMatchData.iMatchState <= 0:
                yield from classDataBaseMgr.getInstance().setMatchResultFinish(objMatchData.strMatchType,strMatchId,timeHelp.getNow())

    else:
        raise exceptionLogic(errorLogic.match_data_not_found)
