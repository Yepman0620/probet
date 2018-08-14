import asyncio
import logging
from ssprotocol import dataHeaderDefine
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.pushDataOpWrapper import coroPushPlayerCoin

@asyncio.coroutine
def handleAwardMatch(objHead:dataHeaderDefine.classResultHead,objDataCenterReq,*args,**kwargs):
    strMatchId = objDataCenterReq.strMatchId
    #strGuessId = objDataCenterReq.strGuessId
    iWinOrLose = objDataCenterReq.iWinOrLose
    iAwardNum = objDataCenterReq.iAwardNum
    iAwardType = objDataCenterReq.iAwardType

    logging.getLogger("result").info("matchId[{}] iWinOrLose[{}] award[{}] result".format(strMatchId,iWinOrLose,iAwardNum))

    objMatchData = yield from classDataBaseMgr.getInstance().getMatchData(strMatchId)
    if objMatchData is None:
        logging.getLogger('result').error("result match data not found [{}]".format(strMatchId))
        return


    try:

        yield from scanAwardMemberTask(objMatchData, iAwardNum, iAwardType,iWinOrLose)

    except Exception as e:
        logging.getLogger('result').error(repr(e))


@asyncio.coroutine
def scanAwardMemberTask(objMatchData,iAwardNum,iAwardType,iWinOrLose):

    try:

        #iNowTime = timeHelp.getNow()
        if iWinOrLose == 0:
            strSKeyNotAward = "matchLoseUniqueAward_{}".format(objMatchData.strMatchId)
            strSKeyAward = "matchLoseUniqueAwarded_{}".format(objMatchData.strMatchId)
        elif iWinOrLose == 1:
            strSKeyNotAward = "matchWinUniqueAward_{}".format(objMatchData.strMatchId)
            strSKeyAward = "matchWinUniqueAwarded_{}".format(objMatchData.strMatchId)
        else:
            strSKeyNotAward = "matchAllUniqueAward_{}".format(objMatchData.strMatchId)
            strSKeyAward = "matchAllUniqueAwarded_{}".format(objMatchData.strMatchId)

        iPopId = yield from classDataBaseMgr.getInstance().getRandomSetItem(strSKeyNotAward)
        logging.getLogger("result").info("pop [{}]".format(iPopId))
        while iPopId != None and len(iPopId) > 0:
            try:
                yield from classDataBaseMgr.getInstance().changeTwoSetList(strSKeyNotAward, strSKeyAward, iPopId)

                strAccountId = iPopId
                objPlayerData,objPlayerLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
                if objPlayerData is None:
                    logging.getLogger("result").error(
                        "player data not found account[{}]".format(strAccountId))
                else:

                    objPlayerData.iGuessCoin += iAwardNum

                    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData,objPlayerLock)

                    # 最后推送一波到客户端
                    yield from coroPushPlayerCoin(objPlayerData.strAccountId,objPlayerData.iGuessCoin)

            except Exception as e:
                logging.getLogger("result").error(repr(e))
            finally:
                iPopId = yield from classDataBaseMgr.getInstance().getRandomSetItem(strSKeyNotAward)

    except Exception as e:
        logging.getLogger('result').error(repr(e))
