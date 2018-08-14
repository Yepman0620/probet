import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import errorLogic,exceptionLogic



@asyncio.coroutine
def handleHttp(dict_param:dict):

    strMatchId = dict_param['strMatchId']
    iHideFlag = dict_param['iHideFlag']


    objMatchData,objMatchDataLock = yield from classDataBaseMgr.getInstance().getMatchDataByLock(strMatchId)
    if objMatchData is None:
        raise exceptionLogic(errorLogic.match_data_not_found)

    objMatchData.iHideFlag = iHideFlag

    yield from classDataBaseMgr.getInstance().setMatchDataByLock(objMatchData,objMatchDataLock)
