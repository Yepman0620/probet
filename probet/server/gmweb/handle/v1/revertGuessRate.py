import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import errorLogic,exceptionLogic



@asyncio.coroutine
def handleHttp(dict_param:dict):

    strGuessId = dict_param['strGuessId']

    objGuessData,objGuessLock = yield from classDataBaseMgr.getInstance().getGuessDataByLock(strGuessId)
    if objGuessData is not None:

        #锁定，拿到当前的返还率
        fTempCalcRefund = 0
        for var_ctr_key, var_ctr_value in objGuessData.dictCTR.items():
            fTempCalcRefund += 1.0 / var_ctr_value.fRate

        fReturnRate = 1.0 / fTempCalcRefund
        fCalcEach = 0.9 / fReturnRate

        for var_ctr_key, var_ctr_value in objGuessData.dictCTR.items():
            var_ctr_value.fRate = round(var_ctr_value.fRate * fCalcEach,2)
            if var_ctr_value.fRate <= 1.0:
                yield from classDataBaseMgr.getInstance().releaseGuessLock(strGuessId, objGuessLock)
                raise exceptionLogic([errorLogic.guess_return_rate_fixUpDownRateFailed_Less1Value.value[0],
                                   errorLogic.guess_return_rate_fixUpDownRateFailed_Less1Value.value[1].format(
                                       var_ctr_key)])

            yield from classDataBaseMgr.getInstance().setGuessDataByLock(objGuessData, objGuessLock)
    else:
        raise exceptionLogic(errorLogic.guess_data_not_found)
