import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import errorLogic,exceptionLogic



@asyncio.coroutine
def handleHttp(dict_param:dict):


    strGuessId = dict_param['strGuessId']
    iFixReturnRate = int(dict_param['iFixReturnRate'])


    objGuessData,objGuessDataLock = yield from classDataBaseMgr.getInstance().getGuessDataByLock(strGuessId)
    if objGuessData is None:
        raise exceptionLogic(errorLogic.guess_data_not_found)

    objGuessData.iFixReturnRate = iFixReturnRate

    yield from classDataBaseMgr.getInstance().setGuessDataByLock(objGuessData,objGuessDataLock)
