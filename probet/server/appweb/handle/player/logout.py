import asyncio
import logging
from datawrapper.dataBaseMgr import classDataBaseMgr
from appweb.logic.pinboLogout import loginout_pinbo
from error.errorCode import exceptionLogic,errorLogic
from lib.timehelp import timeHelp




@asyncio.coroutine
def handleHttp(dict_param: dict):
    """登出"""

    try:
        strAccountId = dict_param["accountId"]
    except Exception as e:
        raise exceptionLogic(errorLogic.client_param_invalid)

    objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
    if objPlayerData is None:
        raise exceptionLogic(errorLogic.player_data_not_found)
    else:
        objPlayerData.strToken = ""
        objPlayerData.iLogoutTime = timeHelp.getNow()
        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData,objLock)

    #调用平博的登出
    objResp = yield from loginout_pinbo(strAccountId)
    if objResp is None:
        logging.error("accountId [{}] logout pinbo failed".format(strAccountId))
