import json
import logging
import aiohttp
import asyncio
from error.errorCode import exceptionLogic, errorLogic
from lib.tokenhelp import tokenhelp

@asyncio.coroutine
def update_status(accountId,status):
    """更改用户状态
    """


    url=tokenhelp.PINBO_URL+"/player/update-status"
    headers=tokenhelp.gen_headers()

    params={}
    params['userCode']='probet.' + accountId
    params['status']=status

    session = aiohttp.ClientSession()
    try:
        with aiohttp.Timeout(10):
            resp = yield from session.get(url=url,params=params,headers=headers,verify_ssl=False)
            if resp.status!=200:
                logging.debug(errorLogic.third_party_error)
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

        return res
    finally:
        if session is not None:
            yield from session.close()
