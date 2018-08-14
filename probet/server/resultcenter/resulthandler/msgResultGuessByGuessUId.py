import asyncio
import logging
import math
from lib.jsonhelp import classJsonDump
from ssprotocol import dataHeaderDefine
from datawrapper.dataBaseMgr import classDataBaseMgr
from resultcenter import result_config
from logic.data.userData import classUserCoinHistory

from lib.timehelp import timeHelp
from logic.enum.enumCoinOp import CoinOp
from logic.enum.enumRank import enumLightList

from gmweb.protocol import gmProtocol
import functools
import json
from logic.logicmgr import orderGeneral
from resultcenter.logicmgr import pushPlayer

@asyncio.coroutine
def handleResultGuess(objHead:dataHeaderDefine.classResultHead,objDataCenterReq,*args,**kwargs):

    logging.info(objDataCenterReq.__dict__)

    strMatchId = objDataCenterReq.strMatchId
    strGuessId = objDataCenterReq.strGuessId
    strWinKey = objDataCenterReq.strWinKey

    iHalfGet = objDataCenterReq.iHalfGet

    logging.getLogger("result").info("matchId[{}] guessId[{}] winKey[{}] result".format(strMatchId,strGuessId,strWinKey))

    objMatchData = yield from classDataBaseMgr.getInstance().getMatchData(strMatchId)
    if objMatchData is None:
        logging.getLogger('result').error("result match data not found [{}]".format(strMatchId))
        return

    objGuessData = yield from classDataBaseMgr.getInstance().getGuessData(strGuessId)
    if objGuessData is None:
        logging.getLogger('result').error("result guess data not found [{}]".format(strGuessId))
        return

    # 获取竞猜比赛的比例
    fRate = objGuessData.dictCTR[strWinKey].fRate
    if fRate >= 10 or fRate <= 0:
        logging.getLogger('result').error("guessId[{}] dictKey[{}] dictContent [{}]".format(strGuessId, strWinKey,
                                                                                            classJsonDump.dumps(
                                                                                                objGuessData.dictCTR)))
    else:
        logging.info(
            "guessId[{}] dictKey[{}] dictContent[{}]".format(strGuessId, strWinKey,
                                                             classJsonDump.dumps(objGuessData.dictCTR)))

    while True:
        try:
            strGuessUId =  yield from classDataBaseMgr.getInstance().getMatchCancelResultGuessUIds(strGuessId)
            yield from doGuessMemberTask(objMatchData,objGuessData,strGuessUId,fRate,strWinKey,iHalfGet)


        except Exception as e:
            logging.getLogger('result').error(repr(e))



@asyncio.coroutine
def doGuessMemberTask(objMatchData,objGuessData,strBetHisUid,fRate,strWinKey,iHalfGet):

    try:
        iNowTime = timeHelp.getNow()

        objBetHis = yield from classDataBaseMgr.getInstance().getBetHistory(strBetHisUid)
        if objBetHis is None:
            logging.getLogger('result').error("bet his is not find [{}]".format(strBetHisUid))
            return


        logging.getLogger("result").debug(
            "begin member account[{}] fRate[{}]".format(objBetHis.strAccountId, fRate))

        if objBetHis.iResult == 9:
            logging.getLogger("result").debug(
                "member account[{}] already getResult".format(objBetHis.strAccountId, objBetHis.strGuessUId))
            yield from classDataBaseMgr.getInstance().releaseBetHistoryLock(objBetHis)
            return

        strTeamKey = objBetHis.strChooseId

        if strTeamKey == strWinKey:
            #猜对了
            if iHalfGet == 0:
                fAddCoin = round(objBetHis.iBetCoin * fRate, 2)
                # 这里给整数
                fAddCoin = math.ceil(fAddCoin)
            else:
                fAddCoin = round(objBetHis.iBetCoin * fRate / 2, 2)
                # 这里给整数
                fAddCoin = math.ceil(fAddCoin)



            objBetHis.iWinCoin = fAddCoin
            fPureAddCoin = objBetHis.iWinCoin - objBetHis.iBetCoin
            if fPureAddCoin < 0:
                fPureAddCoin = 0

            objBetHis.iResult = 9#objGuessData.iGuessState

            yield from classDataBaseMgr.getInstance().setBetHistory(objBetHis)

            objPlayerData, objPlayerDataLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(objBetHis.strAccountId)
            if objPlayerData is None:
                yield from classDataBaseMgr.getInstance().releaseBetHistoryLock(objBetHis)
                logging.getLogger('result').error("result player data not found [{}]".format(objBetHis.strAccountId))
                return

            iBillBefore = objPlayerData.iCoin
            objPlayerData.iCoin += fAddCoin


            iBetRound = -1
            for var_round, var_guess_list in objMatchData.dictGuess.items():
                if objGuessData.strGuessId in var_guess_list:
                    iBetRound = int(var_round)

            yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData,objPlayerDataLock)

            #yield from classDataBaseMgr.getInstance().addMatchWinPlayerId(objMatchData.strMatchId,objPlayerData.strAccountId)


            if iBetRound < 0:
                logging.getLogger("result").error("round not find matchId[{}] [{}]".format(objMatchData.strMatchId,objGuessData.strGuessId))

            dictBill = {
                "billType": "betResultBill",
                "accountId": objPlayerData.strAccountId,
                "matchId": objMatchData.strMatchId,
                "guessName": objGuessData.strGuessName,
                "matchType": objMatchData.strMatchType,
                "guessId": objGuessData.strGuessId,
                "playType": objGuessData.iGuessType,
                "roundNum": iBetRound,
                "supportType": strTeamKey,
                "rate":fRate,
                "betCoinNum": objBetHis.iBetCoin,
                #"nick": objPlayerData.strNick,
                "coinBeforeWin":iBillBefore,
                "coinAfterWin":objPlayerData.iCoin,
                "resultTime":iNowTime,
                "winCoin":fAddCoin,
                "projectType":objMatchData.strMatchType,
                "robot":objBetHis.iRobot,
                "betTime":objBetHis.iTime,
                "betResult":strWinKey,
                "vipLevel":objPlayerData.iLevel,
            }

            logging.getLogger('bill').info(json.dumps(dictBill))

            logging.getLogger("result").debug("end member account[{}] fRate[{}]".format(objBetHis.strAccountId,fRate))

            #最后推送一波到客户端
            yield from pushPlayer.pushMsg(objPlayerData,objBetHis)


        else:

            iNowTime = timeHelp.getNow()

            logging.getLogger("result").debug("begin member account[{}] fRate[{}]".format(objBetHis.strAccountId, fRate))

            objBetHis.iWinCoin = 0
            objBetHis.iResult = 9  # objGuessData.iGuessState

            yield from classDataBaseMgr.getInstance().setBetHistory(objBetHis)

            objPlayerData, objPlayerDataLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(objBetHis.strAccountId)
            if objPlayerData is None:
                yield from classDataBaseMgr.getInstance().releaseBetHistoryLock(objBetHis)
                logging.getLogger('result').error("result player data not found [{}]".format(objBetHis.strAccountId))
                return

            iBillBefore = objPlayerData.iCoin

            objPlayerData.iLoseCoin += objBetHis.iBetCoin
            objPlayerData.iLoseNum += 1

            yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerDataLock)

            #yield from classDataBaseMgr.getInstance().addMatchLostPlayerId(objMatchData.strMatchId,objPlayerData.strAccountId)

            iBetRound = -1
            for var_round, var_guess_list in objMatchData.dictGuess.items():
                if objGuessData.strGuessId in var_guess_list:
                    iBetRound = int(var_round)

            dictBill = {
                "billType": "betResultBill",
                "accountId": objPlayerData.strAccountId,
                "matchId": objMatchData.strMatchId,
                "guessId": objGuessData.strGuessId,
                "matchType": objMatchData.strMatchType,
                "guessName": objGuessData.strGuessName,
                "playType": objGuessData.iGuessType,
                "roundNum": iBetRound,
                "supportType": strTeamKey,
                "rate": fRate,
                "betCoinNum": objBetHis.iBetCoin,
                #"nick": objPlayerData.strNick,
                "coinBeforeWin": iBillBefore,
                "coinAfterWin": objPlayerData.iCoin,
                "resultTime": iNowTime,
                "winCoin": 0,
                "projectType": objMatchData.strMatchType,
                "robot":objBetHis.iRobot,
                "betTime": objBetHis.iTime,
                "betResult": strWinKey,
                "vipLevel":objPlayerData.iLevel,
            }


            logging.getLogger('bill').info(json.dumps(dictBill))

            logging.getLogger("result").debug("end member account[{}] fRate[{}]".format(objBetHis.strAccountId, fRate))

    except Exception as e:
        logging.getLogger('result').error(repr(e))
        logging.getLogger('result').error("guess uid [{}] failed".format(strBetHisUid))

        #TODO lock player retry and push a failed list