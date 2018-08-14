import asyncio
import logging
import math
from ssprotocol import dataHeaderDefine
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.timehelp import timeHelp
import json

@asyncio.coroutine
def handleCancelResultGuessByUId(objHead:dataHeaderDefine.classResultHead,objDataCenterReq,*args,**kwargs):
    strMatchId = objDataCenterReq.strMatchId
    strGuessId = objDataCenterReq.strGuessId

    logging.getLogger("result").info("matchId[{}] guessId[{}] cancel result by guessUId".format(strMatchId,strGuessId))

    objMatchData = yield from classDataBaseMgr.getInstance().getMatchData(strMatchId)
    if objMatchData is None:
        logging.getLogger('result').error("result match data not found [{}]".format(strMatchId))
        return

    objGuessData = yield from classDataBaseMgr.getInstance().getGuessData(strGuessId)
    if objGuessData is None:
        logging.getLogger('result').error("result guess data not found [{}]".format(strGuessId))
        return

    boolLoopFlag = True

    while boolLoopFlag:

        try:
            strGuessUId = yield from classDataBaseMgr.getInstance().getMatchCancelResultGuessUIds(strGuessId)
            if strGuessUId is None:
                logging.getLogger("result").error("guessId:[{}] getResultUId is None".format(objGuessData.strGuessId))
            else:
                yield from doGuessMemberTask(objMatchData, objGuessData, strGuessUId)

        except Exception as e:
            logging.getLogger('result').error(repr(e))



@asyncio.coroutine
def doGuessMemberTask(objMatchData,objGuessData,strBetHisUid):

    try:

        iNowTime = timeHelp.getNow()

        objBetHis = yield from classDataBaseMgr.getInstance().getBetHistory(strBetHisUid)
        if objBetHis is None:
            logging.getLogger('result').error("bet his is not find [{}]".format(strBetHisUid))
            return

        #暂时给这个状态把
        objBetHis.iResult = 8  # objGuessData.iGuessState

        yield from classDataBaseMgr.getInstance().setBetHistory(objBetHis)

        objPlayerData, objPlayerDataLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(objBetHis.strAccountId)
        if objPlayerData is None:
            yield from classDataBaseMgr.getInstance().releaseBetHistoryLock(objBetHis)
            logging.getLogger('result').error("result player data not found [{}]".format(objBetHis.strAccountId))
            return

        iBillBefore = objPlayerData.iCoin


        if objBetHis.iWinCoin != 0:
            #用户如果赢钱了，赢的钱 - 本金
            iAdd = objBetHis.iWinCoin - objBetHis.iBetCoin
            objPlayerData.iCoin -= iAdd
            iCancelCoin = iAdd
            if objPlayerData.iCoin < 0:
                objPlayerData.iCoin = 0

        else:
            objPlayerData.iCoin += objBetHis.iBetCoin
            iCancelCoin = objBetHis.iWinCoin

        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerDataLock)

        iBetRound = -1
        for var_round, var_guess_list in objMatchData.dictGuess.items():
            if objGuessData.strGuessId in var_guess_list:
                iBetRound = int(var_round)

        dictBill = {
            "billType": "betACancelAwardBill",
            "accountId": objPlayerData.strAccountId,
            "accountShortId": objPlayerData.strAccountId,
            "matchId": objMatchData.strMatchId,
            "guessId": objGuessData.strGuessId,
            "playType": objGuessData.iGuessType,
            "roundNum": iBetRound,
            "supportType": objBetHis.strChooseId,
            "betCoinNum": objBetHis.iBetCoin,
            #"nick": objPlayerData.strNick,
            "coinBeforeWin": iBillBefore,
            "coinAfterWin": objPlayerData.iCoin,
            "resultTime": iNowTime,
            "cancelCoin": iCancelCoin,
            "projectType": objMatchData.strMatchType,
            "robot":objBetHis.iRobot,
        }

        logging.getLogger('bill').info(json.dumps(dictBill))

        logging.getLogger("result").debug("end member account[{}] cancel [{}]".format(objBetHis.strAccountId, iCancelCoin))

    except Exception as e:
        logging.getLogger('result').error(repr(e))
        logging.getLogger('result').error("guess uid [{}] failed".format(strBetHisUid))

    #TODO lock player retry and push a failed list