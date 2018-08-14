import asyncio
from error.errorCode import errorLogic,exceptionLogic
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.pushDataOpWrapper import broadCastMatchBasicData

@asyncio.coroutine
def handleHttp(dict_param:dict):

    strMatchId = dict_param["strMatchId"]

    objMatchData,objMatchDataObj = yield from classDataBaseMgr.getInstance().getMatchDataByLock(strMatchId)
    if objMatchData != None:
        objMatchData.iMatchState = 2
        yield from classDataBaseMgr.getInstance().setMatchDataByLock(objMatchData,objMatchDataObj)

        yield from broadCastMatchBasicData([objMatchData], "broadCastPub")
    else:
        raise exceptionLogic(errorLogic.match_data_not_found)
