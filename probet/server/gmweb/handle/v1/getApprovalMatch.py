import asyncio
from gmweb.protocol import gmProtocol
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.timehelp import timeHelp
import logging


@asyncio.coroutine
def handleHttp(dict_param: dict):

    dictApprovalvar_match_data = yield from classDataBaseMgr.getInstance().getPreMatchDataListRetDict()

    respMatchData = []
    for var_match_id,var_match_data in dictApprovalvar_match_data.items():
        objNewData = gmProtocol.classGmMatchData()
        objNewData.strProjectName = var_match_data.strMatchType
        objNewData.strMatchId = var_match_data.strMatchId
        objNewData.iGameState = var_match_data.iMatchState
        objNewData.strActivityName = var_match_data.strMatchName
        try:
            objNewData.strGameStartTime = timeHelp.timestamp2Str(var_match_data.iMatchStartTimestamp)
        except:
            objNewData.strGameStartTime = timeHelp.timestamp2Str(0)

        objNewData.strTeam1Name = var_match_data.strTeamAName
        objNewData.strTeam2Name = var_match_data.strTeamBName
        objNewData.strTeam1Logo = var_match_data.strTeamALogoUrl
        objNewData.strTeam2Logo = var_match_data.strTeamBLogoUrl
        objNewData.iMatchRoundNum = var_match_data.iMatchRoundNum
        objNewData.iHideFlag = var_match_data.iHideFlag
        #objNewData.strTeamAId = var_match_data.strTeamAId
        #objNewData.strTeamBId = var_match_data.strTeamBId
        objNewData.iTeamAScore = var_match_data.iTeamAScore
        objNewData.iTeamBScore = var_match_data.iTeamBScore
        objNewData.iSupportA = var_match_data.iSupportA
        objNewData.iSupportB = var_match_data.iSupportB

        for var_round_num, var_guess_list in var_match_data.dictGuess.items():
            for var_guess_id in var_guess_list:
                objGuessData = yield from classDataBaseMgr.getInstance().getGuessData(var_guess_id)
                objGmPlayData = gmProtocol.classGmPlayData()
                objGmPlayData.strPlayTypeName = objGuessData.strGuessName  # gmProtocol.getTypeMapNameFun(objGuessData.iGuessType,matchData.strTeamAName,matchData.strTeamBName,objGuessData.fSplitScore)
                objGmPlayData.iGuessState = objGuessData.iGuessState
                objGmPlayData.dictTeamInfo = objGuessData.dictCTR
                objGmPlayData.strGuessId = objGuessData.strGuessId
                objGmPlayData.iRoundNum = var_round_num
                objNewData.arrPlayTypeList.append(objGmPlayData)

        respMatchData.append(objNewData)

    logging.debug(classJsonDump.dumps(respMatchData))

    return classJsonDump.dumps(respMatchData)





