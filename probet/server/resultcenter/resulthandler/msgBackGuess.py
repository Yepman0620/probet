import asyncio
import logging
from lib.jsonhelp import classJsonDump
from ssprotocol import dataHeaderDefine
from datawrapper.dataBaseMgr import classDataBaseMgr
from resultcenter import result_config
import functools

from resultcenter.logicmgr import pushPlayer


@asyncio.coroutine
def msgBackGuess(objHead: dataHeaderDefine.classResultHead, objDataCenterReq, *args, **kwargs):
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

    if len(strTeamKey) <= 0:
        #全部玩法退回
        for var_dict_key in objGuessData.dictCTR.keys():
            yield from doFindMemberTask(objMatchData, objGuessData, var_dict_key)

    else:
        yield from doFindMemberTask(objMatchData,objGuessData,strTeamKey)

@asyncio.coroutine
def doFindMemberTask(objMatchData,objGuessData,strTeamKey):

    while True:

        iTaskPos = yield from classDataBaseMgr.getInstance().getSetResultRedisList(objGuessData.strGuessId,strTeamKey,
                                                                                  result_config.batch_get_task_num)

        arrayGuessMember = yield from classDataBaseMgr.getInstance().getResultRedisList(objGuessData.strGuessId, strTeamKey,
                                                                                       iTaskPos - result_config.batch_get_task_num,
                                                                                       iTaskPos)
        if arrayGuessMember is None:
            # 结算这个竞猜数据
            return

        if arrayGuessMember.__len__() <= 0:
            return


        listAsynicoTask = []
        for var_member_uid in arrayGuessMember:
            #objMember = pickle.loads(varMemberBytes)
            objAsynicoTask = asyncio.ensure_future(doGuessMemberTask(objMatchData,objGuessData,var_member_uid.decode(),strTeamKey))
            objAsynicoTask.add_done_callback(functools.partial(memberTaskCallBack, var_member_uid))
            listAsynicoTask.append(objAsynicoTask)

        try:
            yield from asyncio.wait(listAsynicoTask, timeout=200)

        except Exception as e:
            logging.getLogger("result").error(repr(e))


def memberTaskCallBack(member_uid, fut):
    logging.getLogger("result").debug("betHis Uid {} back success".format(member_uid))
    # print(fut.result())


@asyncio.coroutine
def doGuessMemberTask(objMatchData,objGuessData, strBetHisUid, strTeamKey):
    try:

        objBetHis = yield from classDataBaseMgr.getInstance().getBetHistory(strBetHisUid)
        if objBetHis is None:
            logging.getLogger("result").error("bet hist is not find [{}]".format(strBetHisUid))
            yield from classDataBaseMgr.getInstance().releaseBetHistoryLock(strBetHisUid)
            return

        if objBetHis.iResult == 8:
            logging.getLogger("result").error("bet already back [{}]".format(strBetHisUid))
            yield from classDataBaseMgr.getInstance().releaseBetHistoryLock(strBetHisUid)
            return

        objBetHis.iResult = 8

        logging.getLogger("result").debug("begin member account[{}] backNum[{}]".format(objBetHis.strAccountId, objBetHis.iBetCoin))

        yield from classDataBaseMgr.getInstance().setBetHistory(objBetHis)


        objPlayerData, objPlayerDataLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(objBetHis.strAccountId)
        if objPlayerData is None:
            logging.getLogger("result").error("result player data not found [{}]".format(objBetHis.strAccountId))
            return

        objPlayerData.iCoin += objBetHis.iBetCoin

        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerDataLock)


        logging.getLogger("result").debug("end member account[{}] backNum[{}]".format(objBetHis.strAccountId, objBetHis.iBetCoin))

        # 最后推送一波到客户端
        yield from pushPlayer.pushMsg(objPlayerData,objBetHis)

    except Exception as e:
        logging.getLogger("result").error(repr(e))

        # TODO lock player retry and push a failed list