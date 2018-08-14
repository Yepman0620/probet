import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.jsonhelp import classJsonDump
from gmweb.protocol import gmProtocol
from lib.timehelp import timeHelp
from error.errorCode import errorLogic,exceptionLogic


@asyncio.coroutine
def handleHttp(dict_param:dict):

    strGuessId = dict_param['strGuessId']

    objGuessData = yield from classDataBaseMgr.getInstance().getGuessDataByLock(strGuessId)
    if objGuessData is None:
        raise exceptionLogic(errorLogic.guess_data_not_found)

    objNewData = gmProtocol.classGmMatchDetailData()
    objNewData.strGuessId = strGuessId
    objNewData.iTotalJoin = yield from classDataBaseMgr.getInstance().getGuessBetAccountNum(strGuessId)

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
    objNewData.fEquivalenceRatio = 0 if i60TotalBetCoin <= 0 else iTotalBetCoin / i60TotalBetCoin
    fTempCalcRefund = 0
    for var_ctr_key,var_ctr_value in objGuessData.dictCTR.items():
        fTempCalcRefund += 1/(var_ctr_value.fRate)

    objNewData.fRefund = round(1/ fTempCalcRefund,2)

    objNewData.iLimitCoin = objGuessData.iLimitPerAccount
    objNewData.iRefundLock = objGuessData.iFixReturnRate

    listCTRIds = objGuessData.dictCTR.keys()
    for var_ctr_key in listCTRIds:
        listResult = yield from classDataBaseMgr.getInstance().getGraphBetRange(strGuessId,var_ctr_key,gmProtocol.graphRange)
        objNewData.dictGraphItem[var_ctr_key]=listResult

    #拿到所有的，不分类型的记录
    listBetMembersMinute = yield from classDataBaseMgr.getInstance().getGuessMemberStaticListByScore(strGuessId,
                                                                                                        iNowTime,
                                                                                                        iNowTime - 60)
    #近一分钟内的
    for var_ctr_key in listCTRIds:
        tempDict = {}
        for var_graph_rate in gmProtocol.graphRange:
            tempDict[var_graph_rate] = 0
        #te[var_ctr_key] = [i for i in range(0,21)]

        #todo 优化
        for var_bet_member in listBetMembersMinute:

            if var_bet_member['type'] == var_ctr_key:
                #不是本选择项的统计，忽略
                fGraphIndex = gmProtocol.getGraphIndex(var_bet_member['rate'])
                if fGraphIndex in tempDict:
                    tempDict[fGraphIndex] += var_bet_member["num"]
                else:
                    tempDict[fGraphIndex] = var_bet_member["num"]

        objNewData.dictGraphItemLastMinute[var_ctr_key] = [value for key,value in tempDict.items()]

    return classJsonDump.dumps(objNewData)
