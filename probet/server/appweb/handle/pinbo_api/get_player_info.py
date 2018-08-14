import json
import logging
from lib.jsonhelp import classJsonDump
import aiohttp
import asyncio
from error.errorCode import exceptionLogic, errorLogic
from lib.certifytoken import certify_token
from lib.timehelp.timeHelp import getNow
from lib.tokenhelp import tokenhelp
from datawrapper.dataBaseMgr import classDataBaseMgr

@asyncio.coroutine
def handleHttp(request:dict):
    """获取用户信息接口
    """
    url=tokenhelp.PINBO_URL+"/player/info"
    headers=tokenhelp.gen_headers()
    accountId=request.get('accountId','')
    token = request.get('token','')
    source = request.get('source', 'pc')
    if not all([accountId, source]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    certify_token(accountId, token)

    objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(accountId)
    if source == 'pc':
        if objPlayerData.strToken!=token:
            logging.debug(errorLogic.login_token_not_valid)
            raise exceptionLogic(errorLogic.login_token_not_valid)
    elif source == 'app':
        if objPlayerData.strAppToken!=token:
            logging.debug(errorLogic.login_token_not_valid)
            raise exceptionLogic(errorLogic.login_token_not_valid)

    params={}
    params['userCode']='probet.'+accountId

    try:
        with (aiohttp.ClientSession()) as session:
            with aiohttp.Timeout(10):
                resp = yield from session.get(url=url,params=params,headers=headers,verify_ssl=False)
                if resp.status!=200:
                    logging.exception(errorLogic.third_party_error)
                    raise exceptionLogic(errorLogic.third_party_error)

    except Exception as e:
        logging.exception(repr(e))
        raise exceptionLogic(errorLogic.sys_unknow_error)
    else:
        res= yield from resp.read()
        res=json.loads(res.decode())

        code = res.get('code', '')
        if code != '' and (code in errorLogic.pinbo_error_code.keys()):
            logging.debug(code + ":" + errorLogic.pinbo_error_code[code])

            raise exceptionLogic([code, errorLogic.pinbo_error_code[code]])

        availableBalance=res.get("availableBalance")
        if availableBalance is None:
            logging.debug(errorLogic.third_party_error)
            raise exceptionLogic(errorLogic.third_party_error)
        objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(accountId)

        objPlayerData.iPingboCoin = availableBalance * 100
        objPlayerData.iLastPBCRefreshTime=getNow()
        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)
        res['availableBalance']="%.2f"%round(availableBalance,2)
        ret={}
        ret['ret']=errorLogic.success[0]
        ret['data']=res
        ret['retDes']=errorLogic.success[1]

        return classJsonDump.dumps(ret)
