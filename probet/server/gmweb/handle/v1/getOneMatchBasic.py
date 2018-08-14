import asyncio
from gmweb.protocol import gmProtocol
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.timehelp import timeHelp
from lib.jsonhelp import classJsonDump

@asyncio.coroutine
def handleHttp(dict_param:dict):

    strMatchId = dict_param['strMatchId']

    objMatchData = yield from classDataBaseMgr.getInstance().getMatchData(strMatchId)

    objNewData = gmProtocol.classGmMatchData()
    objNewData.strProjectName = objMatchData.strMatchType
    objNewData.strMatchId = objMatchData.strMatchId
    objNewData.iGameState = objMatchData.iMatchState
    objNewData.strActivityName = objMatchData.strMatchName
    objNewData.strGameStartTime = timeHelp.timestamp2Str(objMatchData.iMatchStartTimestamp)
    objNewData.strTeam1Name = objMatchData.strTeamAName
    objNewData.strTeam2Name = objMatchData.strTeamBName
    objNewData.strTeam1Logo = objMatchData.strTeamALogoUrl
    objNewData.strTeam2Logo = objMatchData.strTeamBLogoUrl
    objNewData.iMatchRoundNum = objMatchData.iMatchRoundNum
    objNewData.iHideFlag = objMatchData.iHideFlag
    #objNewData.strTeamAId = objMatchData.strTeamAId
    #objNewData.strTeamBId = objMatchData.strTeamBId
    objNewData.iTeamAScore = objMatchData.iTeamAScore
    objNewData.iTeamBScore = objMatchData.iTeamBScore
    objNewData.iSupportA = objMatchData.iSupportA
    objNewData.iSupportB = objMatchData.iSupportB


    return classJsonDump.dumps(objNewData)


