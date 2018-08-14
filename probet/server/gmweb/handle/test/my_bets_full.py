import json
import logging
import aiohttp
import asyncio
from error.errorCode import exceptionLogic, errorLogic
from lib.tokenhelp import tokenhelp

@asyncio.coroutine
def handleHttp(request:dict):
    # 获取我的投注

    url=tokenhelp.PINBO_URL+'/player/account/my-bets-full'

    headers=tokenhelp.gen_headers()

    data={}
    data['loginId']='probet.test0003'
    data['locale']='zh-cn'

    session=aiohttp.ClientSession()
    try:
        with aiohttp.Timeout(10):
            resp = yield from session.post(url=url, headers=headers, data=data,verify_ssl=False)
            if resp.status != 200:
                raise exceptionLogic(errorLogic.client_param_invalid)

    except Exception as e:
        logging.exception(repr(e))
        raise exceptionLogic(errorLogic.sys_unknow_error)
    else:
        res = yield from resp.read()
        res = json.loads(res.decode())
        code = res.get('code', '')
        if code != '' and (code in errorLogic.pinbo_error_code.keys()):
            logging.debug(code + ":" + errorLogic.pinbo_error_code[code])

            raise exceptionLogic([code, errorLogic.pinbo_error_code[code]])
        return res
    finally:
        if session:
            yield from session.close()
