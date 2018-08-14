import asyncio
import logging
import math
from lib.jsonhelp import classJsonDump
from ssprotocol import dataHeaderDefine
from datawrapper.dataBaseMgr import classDataBaseMgr
from resultcenter import result_config
from logic.data.userData import classUserCoinHistory
from datawrapper.dataBaseMgr import classDataBaseMgr
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
    strTeamKey = objDataCenterReq.strDictKey
    iWinOrLose = objDataCenterReq.iWinOrLose
    iHalfGet = objDataCenterReq.iHalfGet
    strWinKey = objDataCenterReq.strWinKey


    logging.getLogger("result").info("matchId[{}] guessId[{}] dictKey[{}] Win[{}] Half[{}]result".format(strMatchId,strGuessId,strTeamKey,iWinOrLose,iHalfGet))

    #objMatchData = yield from classDataBaseMgr.getInstance().getMatchData(strMatchId)
    objMatchData = yield from classDataBaseMgr.getInstance().getMatchData(strMatchId)
    if objMatchData is None:
        logging.getLogger('result').error("result match data not found [{}]".format(strMatchId))
        return

    #objGuessData = yield from classDataBaseMgr.getInstance().getGuessData(strGuessId)
    objGuessData = yield from classDataBaseMgr.getInstance().getGuessData(strGuessId)
    if objGuessData is None:
        logging.getLogger('result').error("result guess data not found [{}]".format(strGuessId))
        return

    while True:

        iTaskPos =  yield from classDataBaseMgr.getInstance().getSetResultRedisList(strGuessId,strTeamKey,result_config.batch_get_task_num)

        #arrayGuessMember = yield from classDataBaseMgr.getInstance().getResultRedisList(strGuessId, strTeamKey,
        #                                                                               0,
        #                                                                               -1)
        arrayGuessMember = yield from classDataBaseMgr.getInstance().getResultRedisList(strGuessId,strTeamKey,iTaskPos - result_config.batch_get_task_num,iTaskPos)
        if arrayGuessMember is None:
            #结算这个竞猜数据
            return

        if arrayGuessMember.__len__() <= 0:
            return

        #获取竞猜比赛的比例
        fRate = objGuessData.dictCTR[strTeamKey].fRate
        if fRate >= 10 or fRate <= 0:
            logging.getLogger('result').error("guessId[{}] dictKey[{}] dictContent [{}]".format(strGuessId,strTeamKey,classJsonDump.dumps(objGuessData.dictCTR)))
        else:
            logging.info(
                "guessId[{}] dictKey[{}] dictContent[{}]".format(strGuessId, strTeamKey, classJsonDump.dumps(objGuessData.dictCTR)))

        listAsynicoTask = []
        for var_member_uid in arrayGuessMember:

            # TODO 如果把aioredis的连接参数加入了utf-8，这里不需要进行decodes
            objAsynicoTask = asyncio.ensure_future(doGuessMemberTask(objMatchData,objGuessData,var_member_uid.decode(), fRate,strTeamKey,iWinOrLose,iHalfGet,strWinKey))
            objAsynicoTask.add_done_callback(functools.partial(memberTaskCallBack,var_member_uid.decode()))
            listAsynicoTask.append(objAsynicoTask)

        try:
            yield from asyncio.wait(listAsynicoTask,timeout=200)

        except Exception as e:
            logging.getLogger('result').error(repr(e))


def memberTaskCallBack(member_uid,fut):
    logging.getLogger("result").debug("betHis Uid [{}] result success".format(member_uid))
    #print(fut.result())


@asyncio.coroutine
def doGuessMemberTask(objMatchData,objGuessData,strBetHisUid,fRate,strTeamKey,iWinOrLose,iHalfGet,strWinKey):

    try:
        ## 赢了
        if iWinOrLose != 0:

            iNowTime = timeHelp.getNow()

            objBetHis = yield from classDataBaseMgr.getInstance().getBetHistory(strBetHisUid)
            if objBetHis is None:
                logging.getLogger('result').error("bet his is not find [{}]".format(strBetHisUid))
                return

            logging.getLogger("result").debug("begin member account[{}]  fRate[{}]".format(objBetHis.strAccountId,fRate))

            if objBetHis.iResult == 9:
                logging.getLogger("result").debug("member account[{}] already getResult".format(objBetHis.strAccountId,objBetHis.strGuessUId))
                yield from classDataBaseMgr.getInstance().releaseBetHistoryLock(objBetHis)
                return

            fAddCoin = round(objBetHis.iBetCoin * fRate, 2)
            #这里给整数
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
                "guessId": objGuessData.strGuessId,
                "matchType":objMatchData.strMatchType,
                "guessName": objGuessData.strGuessName,
                "roundNum": iBetRound,
                "supportType": strTeamKey,
                "rate":fRate,
                "betCoinNum": objBetHis.iBetCoin,
                #"nick": objPlayerData.strNick,
                "coinBeforeWin":iBillBefore,
                "coinAfterWin":objPlayerData.iCoin,
                "resultTime":iNowTime,
                "winCoin":fAddCoin,    #赢的钱
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

            objBetHis = yield from classDataBaseMgr.getInstance().getBetHistory(strBetHisUid)
            if objBetHis is None:
                logging.getLogger('result').error("bet his is not find [{}]".format(strBetHisUid))
                return

            logging.getLogger("result").debug("begin member account[{}] fRate[{}]".format(objBetHis.strAccountId, fRate))

            objBetHis.iWinCoin = 0 - objBetHis.iBetCoin
            objBetHis.iResult = 9  # objGuessData.iGuessState

            yield from classDataBaseMgr.getInstance().setBetHistory(objBetHis)

            objPlayerData, objPlayerDataLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(objBetHis.strAccountId)
            if objPlayerData is None:
                yield from classDataBaseMgr.getInstance().releaseBetHistoryLock(objBetHis)
                logging.getLogger('result').error("result player data not found [{}]".format(objBetHis.strAccountId))
                return

            iBillBefore = objPlayerData.iCoin


            yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerDataLock)

            #yield from classDataBaseMgr.getInstance().addMatchLostPlayerId(objMatchData.strMatchId,objPlayerData.strAccountId)

            iBetRound = -1
            for var_round, var_guess_list in objMatchData.dictGuess.items():
                if objGuessData.strGuessId in var_guess_list:
                    iBetRound = int(var_round)

            dictBill = {
                "billType": "betResultBill",
                "accountId": objPlayerData.strAccountId,
                'agentId': objPlayerData.strAgentId,
                #"nick": objPlayerData.strNick,
                "guessName": objGuessData.strGuessName,
                "matchType": objMatchData.strMatchType,
                "matchId": objMatchData.strMatchId,
                "guessId": objGuessData.strGuessId,
                "playType": objGuessData.iGuessType,
                "roundNum": iBetRound,
                "supportType": strTeamKey,
                "rate": fRate,
                "betCoinNum": objBetHis.iBetCoin,
                "coinBeforeWin": iBillBefore,
                "coinAfterWin": objPlayerData.iCoin,
                "resultTime": iNowTime,
                "winCoin": 0,      #输的一方为0
                "projectType": objMatchData.strMatchType,
                "robot":objBetHis.iRobot,
                "betTime": objBetHis.iTime,
                "betResult": strWinKey,   #竞猜结果
                "vipLevel":objPlayerData.iLevel,
            }


            logging.getLogger('bill').info(json.dumps(dictBill))

            logging.getLogger("result").debug("end member account[{}] fRate[{}]".format(objBetHis.strAccountId, fRate))

            # 最后推送一波到客户端
            yield from pushPlayer.pushMsg(objPlayerData,objBetHis)

    except Exception as e:
        logging.getLogger('result').error(repr(e))
        logging.getLogger('result').error("guess uid [{}] failed".format(strBetHisUid))

    #TODO lock player retry and push a failed list