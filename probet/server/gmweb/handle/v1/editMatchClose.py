import asyncio
from error.errorCode import errorLogic,exceptionLogic
from datawrapper.dataBaseMgr import classDataBaseMgr



@asyncio.coroutine
def handleHttp(dict_param:dict):
    strMatchId = dict_param["strMatchId"]

    iCloseFlag = int(dict_param["iCloseFlag"])

    objMatchData = yield from classDataBaseMgr.getInstance().getMatchData(strMatchId)
    if objMatchData != None:
        for var_guess_id in objMatchData.arrayGuess:
            objGuessData, objGuessDataLock = yield from classDataBaseMgr.getInstance().getGuessDataByLock(var_guess_id)
            if objGuessData is not None:
                objGuessData.iGuessState = iCloseFlag
                yield from classDataBaseMgr.getInstance().setGuessDataByLock(objGuessData, objGuessDataLock)
    else:
        return exceptionLogic(errorLogic.match_data_not_found)
