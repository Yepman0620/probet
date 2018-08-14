import asyncio
import logging
from ssprotocol import dataHeaderDefine
from datawrapper.dataBaseMgr import classDataBaseMgr
from resultcenter import result_config
import functools


@asyncio.coroutine
def msgNoResultGuess(objHead: dataHeaderDefine.classResultHead, objDataCenterReq, *args, **kwargs):
    strMatchId = objDataCenterReq.strMatchId
    strGuessId = objDataCenterReq.strGuessId
    strTeamKey = objDataCenterReq.strDictKey

    logging.getLogger("result").info("matchId [{}] guessId[{}] dictKey[{}] result".format(strMatchId, strGuessId, strTeamKey))

    objMatchData = yield from classDataBaseMgr.getInstance().getMatchData(strMatchId)
    if objMatchData is None:
        logging.getLogger("result").error("result match data not found [{}]".format(strMatchId))
        return

    # 获取竞猜比赛的比例
    objGuessData = yield from classDataBaseMgr.getInstance().getGuessData(strGuessId)
    if objGuessData is None:
        logging.getLogger("result").error("result guess data not found [{}]".format(strGuessId))
        return

    yield from doFindMemberTask(objMatchData,objGuessData,strTeamKey)

@asyncio.coroutine
def doFindMemberTask(objMatchData,objGuessData):

    while True:
        try:
            strGuessUId = yield from classDataBaseMgr.getInstance().getMatchSetResultGuessUIds(objGuessData.strGuessId)
            if strGuessUId is None:
                logging.getLogger("result").error("guessId:[{}] getResultUId is None".format(objGuessData.strGuessId))
            else:
                yield from doGuessMemberTask(objMatchData,objGuessData,strGuessUId)

        except Exception as e:
            logging.getLogger("result").error(repr(e))




@asyncio.coroutine
def doGuessMemberTask(objMatchData,objGuessData, strBetHisUid):
    try:

        objBetHis = yield from classDataBaseMgr.getInstance().getBetHistory(strBetHisUid)
        if objBetHis is None:
            logging.getLogger("result").error("bet hist is not find [{}]".format(strBetHisUid))
            return

        logging.getLogger("result").debug("begin member account[{}] backNum[{}]".format(objBetHis.strAccountId, objBetHis.iBetCoin))

        objBetHis.iResult = 7
        yield from classDataBaseMgr.getInstance().setBetHistory(objBetHis)
        logging.getLogger("result").debug("end member account[{}] backNum[{}]".format(objBetHis.strAccountId, objBetHis.iBetCoin))

    except Exception as e:
        logging.getLogger("result").error(repr(e))

        # TODO lock player retry and push a failed list