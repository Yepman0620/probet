import asyncio
from error.errorCode import errorLogic,exceptionLogic

from datawrapper.dataBaseMgr import classDataBaseMgr


@asyncio.coroutine
def handleHttp(dict_param:dict):
    strGuessId = dict_param["strGuessId"]
    iGuessState = int(dict_param["iGuessState"])

    objGuessData,objGuessDataLock = yield from classDataBaseMgr.getInstance().getGuessDataByLock(strGuessId)
    if objGuessData != None:
        objGuessData.iGuessState = iGuessState
        #如果关闭状态，则把每个竞猜项都封盘
        yield from classDataBaseMgr.getInstance().setGuessDataByLock(objGuessData,objGuessDataLock)
    else:
        return exceptionLogic(errorLogic.guess_data_not_found)
