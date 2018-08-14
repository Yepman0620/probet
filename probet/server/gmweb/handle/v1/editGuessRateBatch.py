import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import errorLogic,exceptionLogic
from datawrapper.pushDataOpWrapper import broadCastGuessData
from lib.jsonhelp import classJsonDump
from gmweb.protocol import gmProtocol

@asyncio.coroutine
def handleHttp(dict_param:dict):


    strGuessId = dict_param['strGuessId']
    dictModify = dict_param['dictModify']


    objGuessData,objGuessDataLock = yield from classDataBaseMgr.getInstance().getGuessDataByLock(strGuessId)
    if objGuessData is None:
        raise exceptionLogic(errorLogic.guess_data_not_found)

    for var_modify in dictModify:
        objGuessData.dictCTR[var_modify["chooseId"]].fRate = float("%.2f"%round(float(var_modify['rate']),2))

    yield from classDataBaseMgr.getInstance().setGuessDataByLock(objGuessData,objGuessDataLock)

    yield from broadCastGuessData([objGuessData],"broadCastPub")

    objNewData = gmProtocol.classGmMatchBasicData()

    for var_crt_key, var_crt_value in objGuessData.dictCTR.items():
        objNewChooseItem = gmProtocol.classGmChooseBasicData()
        objNewChooseItem.strChooseId = var_crt_key
        objNewChooseItem.strChooseName = var_crt_value.strChooseName
        objNewChooseItem.fTotalBetCoin = var_crt_value.iTotalCoin
        objNewChooseItem.iTotalBetNum = var_crt_value.iTotalBetNum
        objNewChooseItem.fReturnBet = round(var_crt_value.iReturnCoin, 2)
        objNewChooseItem.fRate = round(var_crt_value.fRate, 2) - 1
        objNewData.arrGuessBasicItem.append(objNewChooseItem)
        objNewData.strGuessId = strGuessId

    return classJsonDump.dumps(objNewData)