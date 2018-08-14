import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import errorLogic,exceptionLogic



@asyncio.coroutine
def handleHttp(dict_param:dict):

    strMatchId = dict_param['strMatchId']

    objMatchData,objMatchDataLock = yield from classDataBaseMgr.getInstance().getMatchDataByLock(strMatchId)
    if objMatchData is None:
        raise exceptionLogic(errorLogic.match_data_not_found)

    if 'strTeamAName' in dict_param:
        objMatchData.strTeamAName = dict_param['strTeamAName']

    if 'strTeamBName' in dict_param:
        objMatchData.strTeamBName = dict_param['strTeamBName']

    if 'iMatchStartTimestamp' in dict_param:
        objMatchData.iMatchStartTimestamp = dict_param['iMatchStartTimestamp']

    if 'iMatchEndTimestamp' in dict_param:
        objMatchData.iMatchEndTimestamp = dict_param['iMatchEndTimestamp']

    if 'iTeamAScore' in dict_param:
        objMatchData.iTeamAScore = dict_param['iTeamAScore']

    if 'iTeamBScore' in dict_param:
        objMatchData.iTeamBScore = dict_param['iTeamBScore']

    if 'strMatchName' in dict_param:
        objMatchData.strMatchName = dict_param['strMatchName']

    if 'iMatchRoundNum' in dict_param:
        objMatchData.iMatchRoundNum = dict_param['iMatchRoundNum']

    if 'strTeamALogoUrl' in dict_param:
        objMatchData.strTeamALogoUrl = dict_param['strTeamALogoUrl']

    if 'strTeamBLogoUrl' in dict_param:
        objMatchData.strTeamBLogoUrl = dict_param['strTeamBLogoUrl']

    #if 'strTeamAId' in dict_param:
    #    objMatchData.strTeamAId = dict_param['strTeamAId']

    #if 'strTeamBId' in dict_param:
    #    objMatchData.strTeamBId = dict_param['strTeamBId']

    if 'iSupportA' in dict_param:
        objMatchData.iSupportA = dict_param['iSupportA']

    if 'iSupportB' in dict_param:
        objMatchData.iSupportB = dict_param['iSupportB']



    yield from classDataBaseMgr.getInstance().setMatchDataByLock(objMatchData,objMatchDataLock)
