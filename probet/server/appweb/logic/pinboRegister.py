import json
import logging

import aiohttp
import asyncio
from error.errorCode import exceptionLogic, errorLogic
from lib.tokenhelp import tokenhelp

@asyncio.coroutine
def register_pinbo(accountId):
    """pinbo注册接口
    """
    url='/player/create'
    headers=tokenhelp.gen_headers()

    data={}
    data['loginId']='probet.'+accountId

    session= aiohttp.ClientSession()
    try:
        with aiohttp.Timeout(20):
            resp=yield from session.post(tokenhelp.PINBO_URL+url,headers=headers,data=data,verify_ssl=False)
            if resp.status !=200:
                logging.error("regist pinbo error {} {} {} {}".format(resp.status,tokenhelp.PINBO_URL+url,headers,data))
                raise exceptionLogic(errorLogic.third_party_error)

    except Exception as e:
        logging.error(e)
        raise exceptionLogic(errorLogic.third_party_error)
    else:
        res = yield from resp.read()
        res = json.loads(res.decode())
        code = res.get('code', '')
        if code != '' and (code in errorLogic.pinbo_error_code.keys()):
            logging.debug(code + ":" + errorLogic.pinbo_error_code[code])
            if code == "111":
                raise exceptionLogic(errorLogic.player_id_already_exist)
            raise exceptionLogic([code, errorLogic.pinbo_error_code[code]])

        if res.get('loginId') is None:
            ret = data['loginId']
            return ret
        return res.get('loginId')

    finally:
        if session is not None:
            yield from session.close()

