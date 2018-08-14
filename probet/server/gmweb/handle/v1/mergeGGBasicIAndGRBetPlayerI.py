import asyncio
from lib.jsonhelp import classJsonDump
from gmweb.protocol import gmProtocol
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.timehelp import timeHelp
from error.errorCode import errorLogic,exceptionLogic

@asyncio.coroutine
def handleHttp(dict_param:dict):

    strGuessId = dict_param['strGuessId']

    objGuessData = yield from classDataBaseMgr.getInstance().getGuessData(strGuessId)
    if objGuessData is None:
        raise exceptionLogic(errorLogic.guess_data_not_found)

    objResp = gmProtocol.classGmMergeMatchDetailDataAndRecentPlayerData()

    objMatchDetailData = gmProtocol.classGmMatchDetailData()
    objMatchDetailData.strGuessId = strGuessId
    objMatchDetailData.iTotalJoin = 0#yield from classDataBaseMgr.getInstance().getGuessBetAccountNum(strGuessId)

    iNowTime = timeHelp.getNow()
    list60BetMembers = yield from classDataBaseMgr.getInstance().getGuessMemberStaticListByScore(strGuessId, iNowTime - 60, iNowTime - 60 * 61)
    i60TotalBetCoin = 0
    for var_bet in list60BetMembers:
        i60TotalBetCoin += var_bet['num']

    listBetMembers = yield from classDataBaseMgr.getInstance().getGuessMemberStaticListByScore(strGuessId,
                                                                                                  iNowTime - 60,
                                                                                                  iNowTime - 60 * 61)
    iTotalBetCoin = 0
    for var_bet in listBetMembers:
        iTotalBetCoin += var_bet['num']

    #量比计算
    objMatchDetailData.fEquivalenceRatio = 0 if i60TotalBetCoin <= 0 else iTotalBetCoin / i60TotalBetCoin
    fTempCalcRefund = 0
    for var_ctr_key,var_ctr_value in objGuessData.dictCTR.items():
        fTempCalcRefund += 1/(var_ctr_value.fRate)

    objMatchDetailData.fRefund = round(1/ fTempCalcRefund,2)

    objMatchDetailData.iLimitCoin = objGuessData.iLimitPerAccount
    objMatchDetailData.iRefundLock = objGuessData.iFixReturnRate

    listCTRIds = objGuessData.dictCTR.keys()
    for var_ctr_key in listCTRIds:
        listResult = yield from classDataBaseMgr.getInstance().getGraphBetRange(strGuessId,var_ctr_key,gmProtocol.graphRange)
        objMatchDetailData.dictGraphItem[var_ctr_key]=listResult

    #拿到所有的，不分类型的记录
    listBetMembersMinute = yield from classDataBaseMgr.getInstance().getGuessMemberStaticListByScore(strGuessId,
                                                                                                        iNowTime,
                                                                                                        iNowTime - 60)
    #近一分钟内的
    for var_ctr_key in listCTRIds:
        tempDict = {}
        for var_graph_rate in gmProtocol.graphRange:
            tempDict[var_graph_rate] = 0

        #todo 优化
        for var_bet_member in listBetMembersMinute:

            if var_bet_member['type'] == var_ctr_key:
                #不是本选择项的统计，忽略
                fGraphIndex = gmProtocol.getGraphIndex(var_bet_member['rate'])
                if fGraphIndex in tempDict:
                    tempDict[fGraphIndex] += var_bet_member["num"]
                else:
                    tempDict[fGraphIndex] = var_bet_member["num"]

        objMatchDetailData.dictGraphItemLastMinute[var_ctr_key] = [value for key,value in tempDict.items()]


    iCursor = int(dict_param['iCursor'])
    iLen = yield from classDataBaseMgr.getInstance().getCurrentGuessMemberLen(strGuessId)
    if iCursor <= 0:
        iCursor = iLen - 10
        if iCursor < 0:
            iCursor = 0

    listCurrent = yield from classDataBaseMgr.getInstance().getCurrentGuessMember(strGuessId, iCursor, iLen)
    objRecentPlayerResp = gmProtocol.classGmRecentPlayerData()
    objRecentPlayerResp.iCursor = iLen
    if len(listCurrent) > 0:
        objGuessData = yield from classDataBaseMgr.getInstance().getGuessData(strGuessId)

        objResp.arrChooseName = list(objGuessData.dictCTR.keys())
        for var_member in listCurrent:
            objNewData = gmProtocol.classGmRecentBetItem()
            objNewData.strAccountId = var_member["id"]
            objNewData.strChooseId = var_member["type"]
            objNewData.iBetNum = var_member["num"]
            objNewData.iTime = timeHelp.timestamp2Str(var_member["time"])
            objNewData.fRate = var_member["rate"]
            objRecentPlayerResp.arrCurrentBetInfo.append(objNewData)

    objResp.data1 = objMatchDetailData
    objResp.data2 = objRecentPlayerResp

    return classJsonDump.dumps(objResp)
