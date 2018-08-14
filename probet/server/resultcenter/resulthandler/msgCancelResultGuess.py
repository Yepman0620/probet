import asyncio
import logging
import math
from ssprotocol import dataHeaderDefine
from datawrapper.dataBaseMgr import classDataBaseMgr
from resultcenter import result_config
from logic.data.userData import classUserCoinHistory
from lib.timehelp import timeHelp
from logic.enum.enumCoinOp import CoinOp
from gmweb.protocol import gmProtocol
import traceback
import functools
import json
from logic.logicmgr import orderGeneral

@asyncio.coroutine
def handleCancelResultGuess(objHead:dataHeaderDefine.classResultHead,objDataCenterReq,*args,**kwargs):
    strMatchId = objDataCenterReq.strMatchId
    strGuessId = objDataCenterReq.strGuessId
    strTeamKey = objDataCenterReq.strDictKey
    iBeginTime = objDataCenterReq.iBeginTime
    iEndTime = objDataCenterReq.iEndTime

    logging.getLogger("result").info("matchId[{}] guessId[{}] dictKey[{}] iBegin[{}] iEnd[{}] result".format(strMatchId,strGuessId,strTeamKey,iBeginTime,iEndTime))

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

        iTaskTime =  yield from classDataBaseMgr.getInstance().getSetResultRedisListByScore(strGuessId,strTeamKey,result_config.batch_get_task_time)
        #logging.getLogger("result").info("iTaskTime [{}] iEndTime [{}]".format(iTaskTime,iEndTime))
        if iTaskTime > iEndTime:
            if (iTaskTime - result_config.batch_get_task_time) < iEndTime:
                arrayGuessMember = yield from classDataBaseMgr.getInstance().getResultRedisListByTime(strGuessId,
                                                                                                     strTeamKey,
                                                                                                     iTaskTime - result_config.batch_get_task_time,
                                                                                                     iEndTime)

                logging.getLogger("result").info("iBeginPosTime [{}] iEndPosTime [{}]".format(iTaskTime - result_config.batch_get_task_time, iEndTime))
            else:
                return


        else:
            arrayGuessMember = yield from classDataBaseMgr.getInstance().getResultRedisListByTime(strGuessId, strTeamKey,
                                                                                                 iTaskTime - result_config.batch_get_task_time,
                                                                                                 iTaskTime)
            logging.getLogger("result").info(
                "iBeginPosTime [{}] iEndPosTime [{}]".format(iTaskTime - result_config.batch_get_task_time, iTaskTime))

        if arrayGuessMember is None:
            #结算这个竞猜数据
            continue

        if arrayGuessMember.__len__() <= 0:
            continue

        #获取竞猜比赛的比例
        listAsynicoTask = []
        for var_member_uid in arrayGuessMember:

            # TODO 如果把aioredis的连接参数加入了utf-8，这里不需要进行decode
            objAsynicoTask = asyncio.ensure_future(doGuessMemberTask(objMatchData,objGuessData,var_member_uid.decode(), strTeamKey))
            objAsynicoTask.add_done_callback(functools.partial(memberTaskCallBack,var_member_uid.decode()))
            listAsynicoTask.append(objAsynicoTask)

        try:
            yield from asyncio.wait(listAsynicoTask,timeout=200)

        except Exception as e:
            logging.getLogger('result').error(repr(e))


def memberTaskCallBack(member_uid,fut):
    logging.getLogger("result").debug("betHis Uid [{}] result success".format(member_uid))



@asyncio.coroutine
def doGuessMemberTask(objMatchData,objGuessData,strBetHisUid,strTeamKey):

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
            "supportType": strTeamKey,
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