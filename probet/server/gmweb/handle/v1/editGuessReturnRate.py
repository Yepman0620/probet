import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import errorLogic,exceptionLogic
from datawrapper.pushDataOpWrapper import broadCastGuessData


@asyncio.coroutine
def handleHttp(dict_param:dict):


    strGuessId = dict_param['strGuessId']
    fReturnRate = float(dict_param['strReturnRate'])

    objGuessData,objGuessDataLock = yield from classDataBaseMgr.getInstance().getGuessDataByLock(strGuessId)
    if objGuessData is None:
        raise exceptionLogic(errorLogic.guess_data_not_found)

    #current return rate
    fTempCalcRefund = 0
    for var_ctr_key, var_ctr_value in objGuessData.dictCTR.items():
        fTempCalcRefund += 1 / var_ctr_value.fRate

    #fRefund = round(1 / fTempCalcRefund, 2)
    fCale = (1/fReturnRate) / fTempCalcRefund
    for var_ctr_key, var_ctr_value in objGuessData.dictCTR.items():
        var_ctr_value.fRate *= fCale
        var_ctr_value.fRate = round(var_ctr_value.fRate,2)

    yield from classDataBaseMgr.getInstance().setGuessDataByLock(objGuessData,objGuessDataLock)

    # 推送赔率包到客户的
    yield from broadCastGuessData([objGuessData], "broadCastPub")