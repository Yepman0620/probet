import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import errorLogic,exceptionLogic
from datawrapper.pushDataOpWrapper import broadCastGuessData
from lib.jsonhelp import classJsonDump
from gmweb.protocol import gmProtocol

@asyncio.coroutine
def handleHttp(dict_param:dict):


    strGuessId = dict_param['strGuessId']
    strDictKey = dict_param['strChooseId']

    fGuessRate = -1
    if 'strGuessRate' in dict_param:
        fGuessRate = round(float(dict_param['strGuessRate']),2)


    objGuessData,objGuessDataLock = yield from classDataBaseMgr.getInstance().getGuessDataByLock(strGuessId)
    if objGuessData is None:
        raise exceptionLogic(errorLogic.guess_data_not_found)

    if fGuessRate >=0:
        objGuessData.dictCTR[strDictKey].fRate = float("%.2f"%round(fGuessRate,2))

    yield from classDataBaseMgr.getInstance().setGuessDataByLock(objGuessData,objGuessDataLock)

    # 推送赔率包到客户的
    yield from broadCastGuessData([objGuessData], "broadCastPub")

    objNewData = gmProtocol.classGmMatchBasicData()

    for var_crt_key, var_crt_value in objGuessData.dictCTR.items():
        objNewChooseItem = gmProtocol.classGmChooseBasicData()
        objNewChooseItem.strChooseId = var_crt_key
        objNewChooseItem.strChooseName = var_crt_value.strChooseName
        objNewChooseItem.fTotalBetCoin = var_crt_value.iTotalCoin
        objNewChooseItem.iTotalBetNum = var_crt_value.iTotalBetNum
        objNewChooseItem.fReturnBet = round(var_crt_value.iReturnCoin, 2)
        objNewChooseItem.fRate = var_crt_value.fRate - 1
        objNewData.arrGuessBasicItem.append(objNewChooseItem)
        objNewData.strGuessId = strGuessId

    return classJsonDump.dumps(objNewData)