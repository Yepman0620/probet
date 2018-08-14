import asyncio
from error.errorCode import errorLogic,exceptionLogic
from datawrapper.dataBaseMgr import classDataBaseMgr


@asyncio.coroutine
def handleHttp(dict_param: dict):

    strAgreeMatchId = dict_param['strAgreeMatchId']

    objPreMatchData = yield from classDataBaseMgr.getInstance().getMatchData(strAgreeMatchId)
    if objPreMatchData is None:
        raise exceptionLogic(errorLogic.match_data_not_found)

    yield from classDataBaseMgr.getInstance().agreeApprovalData(objPreMatchData)
