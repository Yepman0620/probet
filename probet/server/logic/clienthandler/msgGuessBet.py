from ssprotocol.dataHeaderDefine import classSSHead
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.playerDataOpWrapper import addPlayerBill
from error.errorCode import exceptionLogic,errorLogic
from csprotocol.protoMatch import protoGuessBetResp
from logic.data.userData import classUserBetHistory,classBetCTR
from logic.logicmgr import checkParamValid as cpv
from lib.timehelp import timeHelp
from gmweb.protocol import gmProtocol
from logic.enum.enumCoinOp import CoinOp
from logic.logicmgr import orderGeneral
from lib.onlineMgr import classOnlineMgr
from lib.pushMgr import classPushMgr
from lib.certifytoken import certify_token
from csprotocol.protocol import pushGuessBet,pushPlayerCoin
from csprotocol.protoMatch import protoPushGuessBetData,protoGuessHistoryItem,protoPushCoinData
import logging
import asyncio
import json


@asyncio.coroutine
def handleGuessBet(objHead:classSSHead,objFbReq:dict):
    objResp = protoGuessBetResp()

    try:
        # 查找用户数据
        if cpv.checkStringEmpty(objHead.strAccountId):
            raise exceptionLogic(errorLogic.player_account_id_empty)

        if not cpv.checkIsString(objHead.strToken):
            raise exceptionLogic(errorLogic.client_param_invalid)

        if cpv.checkStringEmpty(objHead.strToken):
            raise exceptionLogic(errorLogic.client_param_invalid)
        # 将客户端发来的请求参数及值经过处理后获取相应值
        iBetCoin, strMatchId, strBetChooseId, strGuessId, fBetRate, iBetRateIgnore = cpv.getDictStrParam(
            objFbReq, 'iBetCoin','strMatchId','strChooseId', "strGuessId",
            "fBetRate", "iBetRateIgnore")

        if not cpv.checkIsInt(iBetCoin):
            raise exceptionLogic(errorLogic.client_param_invalid)

        #默认转成元单位
        iBetCoin *= 100

        if not cpv.checkIsString(strMatchId):
            raise exceptionLogic(errorLogic.client_param_invalid)

        if not cpv.checkIsString(strBetChooseId):
            raise exceptionLogic(errorLogic.client_param_invalid)

        if not cpv.checkIsString(strGuessId):
            raise exceptionLogic(errorLogic.client_param_invalid)

        if fBetRate is not None:
            fBetRate = float(fBetRate)
            if not cpv.checkIsFloat(fBetRate):
                raise exceptionLogic(errorLogic.client_param_invalid)

        if iBetRateIgnore is not None:
            if not cpv.checkIsInt(iBetRateIgnore):
                raise exceptionLogic(errorLogic.client_param_invalid)

    except:
        raise exceptionLogic(errorLogic.client_param_invalid)

    # 查看最小押注额度
    if iBetCoin < 1000 or iBetCoin > 200000:
        raise exceptionLogic(errorLogic.guess_bet_num_min_limit)

    # 查看是否限制本题的竞猜
    iAlreadyBetNum = yield from classDataBaseMgr.getInstance().getAccountGuessBet(objHead.strAccountId,strGuessId)

    objPlayerData, strPlayerDataLock, objMatchData, objGuess, strGuessLock = yield from classDataBaseMgr.getInstance().getBetData(
        objHead.strAccountId, strMatchId, strGuessId)

    try:
        if objPlayerData is None:  # 用户不存在
            raise exceptionLogic(errorLogic.player_data_not_found)
        """
        if objPlayerData.strToken != objHead.strToken:  # 鉴权信息已过期
            raise exceptionLogic(errorLogic.login_token_not_valid)
        """
        if objMatchData is None:  # 比赛不存在
            raise exceptionLogic(errorLogic.match_data_not_found)

        if objMatchData.iMatchState >= 3:  # 比赛已结束
            raise exceptionLogic(errorLogic.match_state_close)

        if objGuess is None:
            raise exceptionLogic(errorLogic.match_guess_not_found)  # 竞猜不存在
        else:
            if objGuess.iGuessState >= 1:
                raise exceptionLogic(errorLogic.match_guess_state_close)  # 本竞猜已封盘

        if (iAlreadyBetNum + iBetCoin) > objGuess.iLimitPerAccount:
            raise exceptionLogic([errorLogic.guess_bet_num_max_limit[0],
                                  errorLogic.guess_bet_num_max_limit[1].format(iAlreadyBetNum)])

        if strBetChooseId not in objGuess.dictCTR:
            raise exceptionLogic(errorLogic.match_guess_not_found)  # 竞猜未找到


        if objPlayerData.iGuessCoin < iBetCoin:
            raise exceptionLogic(errorLogic.player_coin_not_enough)  # 用户金币不足


        fCurrentRate = round(objGuess.dictCTR[strBetChooseId].fRate, 2)
        # 不忽略赔率变化
        iBillCoinBeforeBet = objPlayerData.iBetCoin
        objPlayerData.iGuessCoin -= iBetCoin


        objNewBetHis = classUserBetHistory()
        # 竞猜id由 uuid4组成
        objNewBetHis.strGuessUId = orderGeneral.generalOrderId()
        objNewBetHis.iBetCoin = iBetCoin
        objNewBetHis.strMatchId = strMatchId
        objNewBetHis.strMatchType = objMatchData.strMatchType
        objNewBetHis.strGuessId = strGuessId
        objNewBetHis.strGuessName = objGuess.strGuessName
        objNewBetHis.iRoundNum = objGuess.iRoundNum
        objNewBetHis.iTime = timeHelp.getNow()
        objNewBetHis.strChooseId = strBetChooseId
        objNewBetHis.strAccountId = objPlayerData.strAccountId
        objNewBetHis.strTeamAName = objMatchData.strTeamAName
        objNewBetHis.strTeamBName = objMatchData.strTeamBName


        # 竞猜id,竞猜信息
        for var_id, var_crt in objGuess.dictCTR.items():
            objBetCTR = classBetCTR()
            objBetCTR.strId = var_id
            objBetCTR.fRate = var_crt.fRate
            objBetCTR.strChooseName = var_crt.strChooseName
            objNewBetHis.dictCTR[var_id] = objBetCTR

        objGuess.dictCTR[strBetChooseId].iTotalCoin += iBetCoin
        objGuess.dictCTR[strBetChooseId].iTotalBetNum += 1
        objGuess.dictCTR[strBetChooseId].iReturnCoin += (iBetCoin * objGuess.dictCTR[strBetChooseId].fRate)

    except:
        # 要把锁都还回去
        if objPlayerData is not None:
            yield from classDataBaseMgr.getInstance().releasePlayerDataLock(objPlayerData.strAccountId,
                                                                                strPlayerDataLock)
        if objGuess is not None:
            yield from classDataBaseMgr.getInstance().releaseGuessLock(objGuess.strGuessId, strGuessLock)

        raise


    # 将当前用户的竞猜信息插入DB
    iNowTime = timeHelp.getNow()
    yield from classDataBaseMgr.getInstance().addBetData(strBetChooseId, objGuess, objPlayerData,
                                                             strGuessLock, strPlayerDataLock, objNewBetHis,
                                                             iNowTime)
    # 推送用户当前的金币
    #yield from pushPlayerCoin(objPlayerData.strAccountId,objPlayerData.iCoin)

    # 添加后台统计柱状图,统一去重用户的押注量,押注用户统计
    fGraphIndex = gmProtocol.getGraphIndex(fCurrentRate)
    yield from classDataBaseMgr.getInstance().addGraphBetRange(objPlayerData.strAccountId, strMatchId, strGuessId,
                                                                   iBetCoin, fGraphIndex, strBetChooseId, iNowTime,
                                                                   fCurrentRate)

    # 写入金币消耗日志
    if objGuess.iRoundNum == 0:
        coinHisDes = "本场比赛\n {}\n {}".format(objGuess.strGuessName,objGuess.dictCTR[strBetChooseId].strChooseName)
    else:
        coinHisDes = "{}局\n {}\n {}".format(objGuess.iRoundNum,objGuess.strGuessName,objGuess.dictCTR[strBetChooseId].strChooseName)

    #gmProtocol.gameTypeMap.get(objMatchData.strMatchType)

    # 给用户推送一下投注单
    yield from pushPlayerData(objPlayerData,objNewBetHis)

    logging.getLogger('logic').info("bet account[{}] ip[{}]".format(objPlayerData.strAccountId, objHead.strClientIp))

    dictBill = {
        'billType': "betBill",
        'betHisUId': objNewBetHis.strGuessUId,
        'accountId': objPlayerData.strAccountId,
        'agentId':objPlayerData.strAgentId,
        #'nick': objPlayerData.strNick,
        'matchId': objMatchData.strMatchId,
        'guessId': objGuess.strGuessId,
        'roundNum': objGuess.iRoundNum,
        'supportType': strBetChooseId,
        'betCoinNum': iBetCoin,        #竞猜金额
        'coinBeforeBet': iBillCoinBeforeBet,
        'coinAfterBet': objPlayerData.iBetCoin,
        'projectType': objMatchData.strMatchType,
        'betTime': timeHelp.getNow(),
    }

    logging.getLogger('bill').info(json.dumps(dictBill))

    return objResp


@asyncio.coroutine
def pushPlayerData(objPlayerData,objBetHisData):

    dictOnlineInfo = yield from classOnlineMgr.getInstance().getOnlineClient(objPlayerData.strAccountId)
    if dictOnlineInfo is not None:
        # 没在线，不用推送了
        objPushSSHead = classSSHead()
        objPushSSHead.strAccountId = objPlayerData.strAccountId
        objPushSSHead.strMsgId = pushGuessBet
        objPushSSHead.strClientUdid = dictOnlineInfo['connectUid']

        objRsp = protoPushGuessBetData()
        objHisItem = protoGuessHistoryItem(objBetHisData)
        objRsp.listGuessBetList.append(objHisItem)

        yield from classPushMgr.getInstance().push(dictOnlineInfo['host'], dictOnlineInfo['groupId'],
                                                   objPushSSHead, objRsp)

        # 推送一下金钱
        objPushSSHead.strMsgId = pushPlayerCoin
        objRsp = protoPushCoinData()
        objRsp.iCoin = "%.2f"%round(objPlayerData.iGuessCoin/100,2)

        yield from classPushMgr.getInstance().push(dictOnlineInfo['host'], dictOnlineInfo['groupId'],
                                                   objPushSSHead, objRsp)