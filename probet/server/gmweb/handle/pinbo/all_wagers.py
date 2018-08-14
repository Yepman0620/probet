import json
import logging
import time
import asyncio
import aiohttp

from error.errorCode import errorLogic, exceptionLogic
from lib.tokenhelp import tokenhelp

@asyncio.coroutine
def handleHttp(request:dict):
    # 获取所有投注
    url=tokenhelp.PINBO_URL+'/report/all-wagers'

    headers=tokenhelp.gen_headers()

    params={}
    params['dateFrom']= request["begin"]#'2018-05-18 10:00:00'
    params['dateTo']= request["end"]#'2018-05-19 10:00:00'

    # 需要校验数据
    session= aiohttp.ClientSession()
    try:
        with aiohttp.Timeout(10):
            resp=yield from session.get(url=url, headers=headers, params=params,verify_ssl=False)
            print(resp.status)
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
