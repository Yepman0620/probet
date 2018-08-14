import asyncio
from gmweb.protocol import gmProtocol
from error.errorCode import errorLogic,exceptionLogic

from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.timehelp import timeHelp
from lib.jsonhelp import classJsonDump

@asyncio.coroutine
def handleHttp(dict_param:dict):


    iPageSize = int(dict_param['iPageSize'])
    iPageNum = int(dict_param['iPageNum'])
    iPageNum -= 1

    iBeginIndex = iPageNum* iPageSize
    iEndIndex = iBeginIndex + iPageSize


    listMatchIds,iCount = yield from classDataBaseMgr.getInstance().getMatchCancelAwardedList(iBeginIndex,iEndIndex)
    listMatchData = yield from classDataBaseMgr.getInstance().getMatchDataList(listMatchIds)
    objResp =  gmProtocol.classGmMatchTotal()
    objResp.iTotalNum = iCount

    if len(listMatchData) != len(listMatchData):
        raise exceptionLogic(errorLogic.sys_unknow_error)

    for iIndex in range(0,len(listMatchData)):
        matchData = listMatchData[iIndex]

        objNewData = gmProtocol.classGmMatchData()
        objNewData.strProjectName = matchData.strMatchType
        objNewData.strMatchId = matchData.strMatchId
        objNewData.iGameState = matchData.iMatchState
        objNewData.strActivityName = matchData.strMatchName
        objNewData.strGameStartTime = timeHelp.timestamp2Str(matchData.iMatchStartTimestamp)
        objNewData.strTeam1Name = matchData.strTeamAName
        objNewData.strTeam2Name = matchData.strTeamBName
        objNewData.strTeam1Logo = matchData.strTeamALogoUrl
        objNewData.strTeam2Logo = matchData.strTeamBLogoUrl
        objNewData.iMatchRoundNum = matchData.iMatchRoundNum
        objNewData.iHideFlag = matchData.iHideFlag
        #objNewData.strTeamAId = matchData.strTeamAId
        #objNewData.strTeamBId = matchData.strTeamBId
        objNewData.iTeamAScore = matchData.iTeamAScore
        objNewData.iTeamBScore = matchData.iTeamBScore
        objNewData.iSupportA = matchData.iSupportA
        objNewData.iSupportB = matchData.iSupportB


        objNewData.iAwardFlag = matchData.iAwardFlag
        objNewData.iAwardNum = matchData.iAwardNum
        objNewData.iAwardType = matchData.iAwardType
        objNewData.iWinOrLose = matchData.iWinOrLose
        objNewData.iCancelResultFlag = matchData.iCancelResultFlag
        objNewData.iCancelResultBeginTime = matchData.iCancelResultBeginTime
        objNewData.iCancelResultEndTime = matchData.iCancelResultEndTime

        objResp.arrMatchData.append(objNewData)

    return classJsonDump.dumps(objResp)
