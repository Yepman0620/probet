import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic,errorLogic


@asyncio.coroutine
def handleHttp(request: dict):

    strTestToke = request.get("token",None)
    if strTestToke is None:
        raise exceptionLogic(errorLogic.token_not_valid)
    else:
        if strTestToke != "asdfghjkl123!@#":
            raise exceptionLogic(errorLogic.token_not_valid)

    strAccountId = request.get("strAccountId")
    objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(strAccountId)

    return classJsonDump.dumps({"token":"asdfghjkl123!@#","playerData":objPlayerData})