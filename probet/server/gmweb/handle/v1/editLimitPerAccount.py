import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.jsonhelp import classJsonDump
from gmweb.protocol import gmProtocol
from lib.timehelp import timeHelp

@asyncio.coroutine
def handleHttp(dict_param:dict):

    strGuessId = dict_param['strGuessId']
    iLimit = int(dict_param['iLimit'])

    objGuessData,objGuesslock = yield from classDataBaseMgr.getInstance().getGuessDataByLock(strGuessId)

    objGuessData.iLimitPerAccount = iLimit
    yield from classDataBaseMgr.getInstance().setGuessDataByLock(objGuessData,objGuesslock)
