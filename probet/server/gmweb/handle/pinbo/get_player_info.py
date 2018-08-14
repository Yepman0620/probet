import json
import logging
import aiohttp
import asyncio

from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib.timehelp.timeHelp import getNow
from lib.tokenhelp import tokenhelp

@asyncio.coroutine
def get_pingbo_player_info(accountId):
    """获取用户信息接口
    """
    url=tokenhelp.PINBO_URL+"/player/info"
    headers=tokenhelp.gen_headers()

    params={}
    params['userCode']='probet.' + accountId

    try:
        with (aiohttp.ClientSession()) as session:
            with aiohttp.Timeout(2):
                resp = yield from session.get(url=url,params=params,headers=headers,verify_ssl=False)
                if resp.status!=200:
                    logging.debug(errorLogic.third_party_error)
                    raise exceptionLogic(errorLogic.third_party_error)

    except Exception as e:
        logging.exception(repr(e))
        raise exceptionLogic(errorLogic.sys_unknow_error)
    else:
        res= yield from resp.read()
        res= json.loads(res.decode())

        code = res.get('code', '')
        if code != '' and (code in errorLogic.pinbo_error_code.keys()):
            logging.debug(code + ":" + errorLogic.pinbo_error_code[code])
            raise exceptionLogic([code, errorLogic.pinbo_error_code[code]])

        availableBalance = res.get("availableBalance")
        if availableBalance is None:
            logging.debug(errorLogic.third_party_error)
            raise exceptionLogic(errorLogic.third_party_error)

        objPlayerData,objLock=yield from classDataBaseMgr.getInstance().getPlayerDataByLock(accountId)
        if objPlayerData is None:
            logging.debug("account: [{}] is not Exist".format(objPlayerData.strAccountId))
        else:
            objPlayerData.iPingboCoin=availableBalance * 100
            objPlayerData.iLastPBCRefreshTime=getNow()
            yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData,objLock)

        return res

