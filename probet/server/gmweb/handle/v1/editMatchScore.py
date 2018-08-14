import asyncio
from error.errorCode import errorLogic,exceptionLogic
from lib.timehelp import timeHelp
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.pushDataOpWrapper import broadCastMatchBasicData

@asyncio.coroutine
def handleHttp(dict_param:dict):

    strMatchId = dict_param['strMatchId']
    dictScores = dict_param['dictScores']

    objMatchData,objMatchDataLock = yield from classDataBaseMgr.getInstance().getMatchDataByLock(strMatchId)
    if objMatchData is None:
        raise exceptionLogic(errorLogic.match_data_not_found)

    objMatchData.iTeamAScore = dictScores['iAScore']
    objMatchData.iTeamBScore = dictScores['iBScore']
    #objMatchData.iMatchState = 3
    #objMatchData.iMatchEndTimestamp = timeHelp.getNow()

    yield from classDataBaseMgr.getInstance().setMatchDataByLock(objMatchData,objMatchDataLock)

    yield from broadCastMatchBasicData([objMatchData],"broadCastPub")
