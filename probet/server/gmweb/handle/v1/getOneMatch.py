import asyncio
from gmweb.protocol import gmProtocol
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.timehelp import timeHelp
import logging
from lib.jsonhelp import classJsonDump

@asyncio.coroutine
def handleHttp(dict_param:dict):

    strMatchId = dict_param['strMatchId']

    objMatchData = yield from classDataBaseMgr.getInstance().getMatchData(strMatchId)
    #objMatchAssertData,objMatchAssertlock = yield from singletonDefine.g_obj_GmDataMgr.getMatchAssertData(strMatchId,False)

    objNewData = gmProtocol.classGmMatchData()
    #objNewData.strProjectName = strProjectName
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

    for var_round_num, var_guess_list in objMatchData.dictGuess.items():
        for var_guess_id in var_guess_list:
            objGuessData = yield from classDataBaseMgr.getInstance().getGuessData(var_guess_id)
            objGmPlayData = gmProtocol.classGmPlayData()
            objGmPlayData.strPlayTypeName = objGuessData.strGuessName
            objGmPlayData.iGuessState = objGuessData.iGuessState
            objGmPlayData.dictTeamInfo = objGuessData.dictCTR
            objGmPlayData.strGuessId = objGuessData.strGuessId
            objGmPlayData.iRoundNum = var_round_num
            objGmPlayData.iHideFlag = objGuessData.iHideFlag
            objGmPlayData.strGuessResult = objGuessData.strGuessResult
            objNewData.arrPlayTypeList.append(objGmPlayData)

    return classJsonDump.dumps(objNewData)


