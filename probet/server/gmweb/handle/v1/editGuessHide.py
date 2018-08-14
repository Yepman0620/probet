import asyncio
from error.errorCode import errorLogic,exceptionLogic

from datawrapper.dataBaseMgr import classDataBaseMgr

@asyncio.coroutine
def handleHttp(dict_param:dict):

    strGuessId = dict_param['strGuessId']
    iHideFlag = dict_param["iHideFlag"]

    objGuessData, objGuessDataLock = yield from classDataBaseMgr.getInstance().getGuessDataByLock(strGuessId)
    if objGuessData is None:
        raise exceptionLogic(errorLogic.guess_data_not_found)

    objGuessData.iHideFlag = iHideFlag

    yield from classDataBaseMgr.getInstance().setGuessDataByLock(objGuessData, objGuessDataLock)
