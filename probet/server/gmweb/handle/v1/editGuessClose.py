import asyncio
from error.errorCode import errorLogic,exceptionLogic
from datawrapper.pushDataOpWrapper import broadCastGuessData
from datawrapper.dataBaseMgr import classDataBaseMgr



@asyncio.coroutine
def handleHttp(dict_param:dict):
    strGuessId = dict_param["strGuessId"]
    iCloseFlag = int(dict_param["iCloseFlag"])

    objGuessData,objGuessDataLock = yield from classDataBaseMgr.getInstance().getGuessDataByLock(strGuessId)
    if objGuessData != None:
        objGuessData.iGuessState = iCloseFlag

        yield from classDataBaseMgr.getInstance().setGuessDataByLock(objGuessData,objGuessDataLock)

        yield from broadCastGuessData([objGuessData],"broadCastPub")
    else:
        exceptionLogic(errorLogic.guess_data_not_found)
