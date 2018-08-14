import asyncio
from lib.jsonhelp import classJsonDump
from gmweb.protocol import gmProtocol
from error.errorCode import errorLogic,exceptionLogic
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.pushDataOpWrapper import broadCastGuessData
import copy

@asyncio.coroutine
def handleHttp(dict_param:dict):

    strGuessId = dict_param['strGuessId']
    strChooseId = dict_param["strChooseId"]
    iUpRate = float(dict_param["strUpRate"])

    objGuessData,objGuessLock = yield from classDataBaseMgr.getInstance().getGuessDataByLock(strGuessId)
    if objGuessData is not None:
        objCTR = objGuessData.dictCTR.get(strChooseId)
        if objCTR is None:
            yield from classDataBaseMgr.getInstance().releaseGuessLock(strGuessId, objGuessLock)
            raise exceptionLogic(errorLogic.guess_data_not_found)
        else:

            #查看是否固定返还率
            if True:#objGuessData.iFixReturnRate != 0:
                #锁定，拿到当前的返还率
                fTempCalcRefund = 0
                for var_ctr_key, var_ctr_value in objGuessData.dictCTR.items():
                    fTempCalcRefund += 1.0 / var_ctr_value.fRate

                # 原来的值
                fOldCalc = copy.deepcopy(fTempCalcRefund)
                fOldCalc = fOldCalc - (1.0 / objCTR.fRate)

                objCTR.fRate = float("%.2f"%round(objCTR.fRate + abs(objCTR.fRate - 1) * iUpRate,2))
                fTempCalcRefund =  fTempCalcRefund - (1.0 / objCTR.fRate)

                fCalcEach = fTempCalcRefund / fOldCalc
                for var_ctr_key, var_ctr_value in objGuessData.dictCTR.items():
                    if var_ctr_key == strChooseId:
                        pass
                    else:
                        var_ctr_value.fRate = float("%.2f"%round(var_ctr_value.fRate * 1.0 / fCalcEach,2))

                    if var_ctr_value.fRate <= 1.0:
                        yield from classDataBaseMgr.getInstance().releaseGuessLock(strGuessId, objGuessLock)
                        raise exceptionLogic([errorLogic.guess_return_rate_fixUpDownRateFailed_Less1Value.value[0],
                                           errorLogic.guess_return_rate_fixUpDownRateFailed_Less1Value.value[1].format(
                                               var_ctr_key)])

            else:
                objCTR.fRate = float("%.2f"%round(objCTR.fRate + abs(objCTR.fRate - 1) * iUpRate,2))
                if objCTR.fRate <= 1.0:
                    yield from classDataBaseMgr.getInstance().releaseGuessLock(strGuessId, objGuessLock)
                    raise exceptionLogic([errorLogic.guess_return_rate_fixUpDownRateFailed_Less1Value.value[0],
                                       errorLogic.guess_return_rate_fixUpDownRateFailed_Less1Value.value[1].format(
                                           strChooseId)])

            yield from classDataBaseMgr.getInstance().setGuessDataByLock(objGuessData, objGuessLock)

            #推送赔率包到客户的
            yield from broadCastGuessData([objGuessData],"broadCastPub")

    else:
        raise exceptionLogic(errorLogic.guess_data_not_found)

    objNewData = gmProtocol.classGmMatchBasicData()

    for var_crt_key,var_crt_value in objGuessData.dictCTR.items():
        objNewChooseItem = gmProtocol.classGmChooseBasicData()
        objNewChooseItem.strChooseId = var_crt_key
        objNewChooseItem.strChooseName = var_crt_value.strChooseName
        objNewChooseItem.fTotalBetCoin = var_crt_value.iTotalCoin
        objNewChooseItem.iTotalBetNum = var_crt_value.iTotalBetNum
        objNewChooseItem.fReturnBet = round(var_crt_value.iReturnCoin,2)
        objNewChooseItem.fRate = float("%.2f"%round(var_crt_value.fRate,2)) - 1
        objNewData.arrGuessBasicItem.append(objNewChooseItem)
        objNewData.strGuessId = strGuessId

    return classJsonDump.dumps(objNewData)

