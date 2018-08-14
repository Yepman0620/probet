import asyncio
import logging
from lib.jsonhelp import classJsonDump
from ssprotocol import dataHeaderDefine
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.pushDataOpWrapper import coroPushPlayerCoin

@asyncio.coroutine
def handleCancelAwardMatch(objHead:dataHeaderDefine.classResultHead,objDataCenterReq,*args,**kwargs):
    strMatchId = objDataCenterReq.strMatchId
    #strGuessId = objDataCenterReq.strGuessId
    iWinOrLose = objDataCenterReq.iWinOrLose
    iAwardNum = objDataCenterReq.iAwardNum
    iAwardType = objDataCenterReq.iAwardType

    logging.getLogger("result").info("matchId[{}]  winOrLose[{}] cancel award[{}] result".format(strMatchId,iWinOrLose,iAwardNum))

    objMatchData = yield from classDataBaseMgr.getInstance().getMatchData(strMatchId)
    if objMatchData is None:
        logging.getLogger('result').error("result match data not found [{}]".format(strMatchId))
        return


    try:
        #yield from asyncio.get_event_loop().call_soon(scanAwardMemberTask, objMatchData, objGuessData,iAwardCoin,strTeamKey)
        yield from scanAwardMemberTask(objMatchData, iAwardNum,iAwardType, iWinOrLose)

        #yield from asyncio.gather(fu)
    except Exception as e:
        logging.getLogger('result').error(repr(e))


@asyncio.coroutine
def scanAwardMemberTask(objMatchData,iAwardNum,iAwardType,iWinOrLose):

    try:

        #iNowTime = timeHelp.getNow()
        if iWinOrLose == 0:
            strSKeyAward = "matchLoseUniqueAward".format(objMatchData.strMatchId)
            strSKeyNotAward = "matchLoseUniqueAwarded".format(objMatchData.strMatchId)
        elif iWinOrLose == 1:
            strSKeyAward = "matchWinUniqueAward".format(objMatchData.strMatchId)
            strSKeyNotAward = "matchWinUniqueAwarded".format(objMatchData.strMatchId)
        else:
            strSKeyAward = "matchAllUniqueAward".format(objMatchData.strMatchId)
            strSKeyNotAward = "matchAllUniqueAwarded".format(objMatchData.strMatchId)

        iPopId = yield from classDataBaseMgr.getInstance().getRandomSetItem(strSKeyAward)
        logging.getLogger("result").info("pop [{}]".format(iPopId))

        while iPopId != None and len(iPopId) > 0:
            try:
                yield from classDataBaseMgr.getInstance().changeTwoSetList(strSKeyAward,strSKeyNotAward, iPopId)

                strAccountId = iPopId
                objPlayerData,objPlayerLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
                if objPlayerData is None:
                    logging.getLogger("result").error(
                        "player data not found account[{}]".format(strAccountId))
                else:
                    if iAwardType == 0:
                        objPlayerData.iCoin -= iAwardNum
                    else:
                        objPlayerData.fDiamond -= iAwardNum

                    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData,objPlayerLock)


                    # 最后推送一波到客户端
                    #yield from pushPlayer.pushMsg(objPlayerData,objBetHis)
                    yield from coroPushPlayerCoin(objPlayerData.strAccountId, objPlayerData.iGuessCoin)


            except Exception as e:
                logging.getLogger("result").error(repr(e))
            finally:
                iPopId = yield from classDataBaseMgr.getInstance().getRandomSetItem(strSKeyAward)

    except Exception as e:
        logging.getLogger('result').error(repr(e))
