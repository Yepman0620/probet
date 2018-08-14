import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
#from datawrapper.playerDataOpWrapper import addPlayerCoinByAccountId
from error.errorCode import errorLogic,exceptionLogic
from logic.data.userData import classUserCoinHistory
from lib.timehelp import timeHelp
from logic.logicmgr import orderGeneral
from logic.enum.enumCoinOp import CoinOp
from gmweb.protocol import gmProtocol

@asyncio.coroutine
def handleHttp(dict_param:dict):

    strAccountId = dict_param['strAccountId']
    strBetHisUId = dict_param['strBetHisUId']

    objBetHis,objBetHisLock = yield from classDataBaseMgr.getInstance().getBetHistoryData(strBetHisUId)
    if objBetHis is None:
        raise exceptionLogic(errorLogic.bet_hist_data_not_found)

    objPlayerData,objPlayerLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
    if objPlayerData is None:
        raise exceptionLogic(errorLogic.player_data_not_found)

    #同guess state 状态
    if objBetHis.iResult == 8:
        #yield from classDataBaseMgr.getInstance().releasePlayerDataLock(objPlayerData.strAccountId, objPlayerLock)
        raise exceptionLogic(errorLogic.bet_his_data_already_back)

    objBetHis.iResult = 8

    #yield from addPlayerCoinByAccountId(strAccountId,objBetHis.iBetCoin)
    objPlayerData.iCoin += objBetHis.iBetCoin
    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerLock)


    objNewPayHis = classUserCoinHistory()
    objNewPayHis.iTime = timeHelp.getNow()
    objNewPayHis.strOrderId = orderGeneral.generalOrderId()
    objNewPayHis.fCoinNum = objBetHis.iBetCoin
    objNewPayHis.iOpType = CoinOp.coinOpBet

    objMatchData = yield from classDataBaseMgr.getInstance().getMatchDataByLock(objBetHis.strMatchId)
    if objMatchData is None:
        return

    objGuessData = yield from classDataBaseMgr.getInstance().getGuessDataByLock(objBetHis.strGuessId)
    if objGuessData is None:
        return

    iBetRound = -1

    for var_round, var_guess_list in objMatchData.dictGuess.items():
        if objGuessData.strGuessId in var_guess_list:
            iBetRound = int(var_round)

    if iBetRound == 0:
        objNewPayHis.strDes = "{}\n {} vs {}\n 本场比赛\n {}\n {}".format(gmProtocol.gameTypeMap.get(objMatchData.strMatchType),
                                                                      objMatchData.strTeamAName,
                                                                      objMatchData.strTeamBName,
                                                                      objGuessData.strGuessName,
                                                                      objGuessData.dictCTR[objBetHis.strChooseId].strChooseName)
    else:
        objNewPayHis.strDes = "{}\n {} vs {}\n {}局\n {}\n {}".format(gmProtocol.gameTypeMap.get(objMatchData.strMatchType),
                                                                     objMatchData.strTeamAName,
                                                                     objMatchData.strTeamBName,
                                                                     iBetRound,
                                                                     objGuessData.strGuessName,
                                                                     objGuessData.dictCTR[objBetHis.strChooseId].strChooseName)

    yield from classDataBaseMgr.getInstance().addPlayerCoinRecord(objBetHis.strAccountId, objNewPayHis)


    yield from classDataBaseMgr.getInstance().setBetHistory(objBetHis)
    #yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData,objPlayerLock)

