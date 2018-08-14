import asyncio
from error.errorCode import errorLogic,exceptionLogic
from datawrapper.dataBaseMgr import classDataBaseMgr

@asyncio.coroutine
def handleHttp(dict_param:dict):
    strMatchId = dict_param["strMatchId"]

    objMatchData = yield from classDataBaseMgr.getInstance().getMatchData(strMatchId)
    if objMatchData != None:
        for var_guess_id in objMatchData.arrayGuess:
            objGuessData, objGuessDataLock = yield from classDataBaseMgr.getInstance().getGuessData(var_guess_id)
            if objGuessData is not None:
                yield from classDataBaseMgr.getInstance().delGuessData(var_guess_id)

        yield from classDataBaseMgr.getInstance().delMatchData(strMatchId)
        #TODO 还有一些需要删除的东西
    else:
        raise exceptionLogic(errorLogic.match_data_not_found)
