import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.jsonhelp import classJsonDump
from gmweb.protocol import gmProtocol
from error.errorCode import exceptionLogic,errorLogic


@asyncio.coroutine
def handleHttp(dict_param:dict):

    strMatchId = dict_param['strMatchId']
    iRoundNum = int(dict_param["iRoundNum"])

    objMatchData = yield from classDataBaseMgr.getInstance().getMatchData(strMatchId)
    if objMatchData is None:
        raise exceptionLogic(errorLogic.match_data_not_found)

    objNewData = gmProtocol.classGmMatchBasicData()
    objNewData.strMatchId = strMatchId
    listGuessId = objMatchData.dictGuess.get(iRoundNum)
    if listGuessId is None or len(listGuessId) <= 0:
        return classJsonDump.dumps(objNewData)

    dictGuessData = yield from classDataBaseMgr.getInstance().getGuessDataListRetDict(listGuessId)

    for var_guess_key,var_guess_data in dictGuessData.items():
        objNewBasicItem = gmProtocol.classGmMatchBasicItem()
        objNewBasicItem.strGuessId = var_guess_data.strGuessId
        objNewBasicItem.strGuessName = var_guess_data.strGuessName
        objNewBasicItem.iGuessState = var_guess_data.iGuessState
        #给客户的返回这个结果对应的选择名称
        if len(var_guess_data.strGuessResult) > 0:
            objNewBasicItem.strResult = var_guess_data.dictCTR[var_guess_data.strGuessResult].strChooseName

        for var_crt_key,var_crt_value in var_guess_data.dictCTR.items():
            objNewChooseItem = gmProtocol.classGmChooseBasicData()
            objNewChooseItem.strChooseId = var_crt_key
            objNewChooseItem.strChooseName = var_crt_value.strChooseName
            objNewChooseItem.fTotalBetCoin = var_crt_value.iTotalCoin
            objNewChooseItem.iTotalBetNum = var_crt_value.iTotalBetNum
            objNewChooseItem.fReturnBet = round(var_crt_value.iReturnCoin,2)
            objNewChooseItem.fRate = round(var_crt_value.fRate - 1,2)

            objNewBasicItem.arrChooseBasicData.append(objNewChooseItem)
        objNewData.arrGuessBasicItem.append(objNewBasicItem)

    return classJsonDump.dumps(objNewData)


