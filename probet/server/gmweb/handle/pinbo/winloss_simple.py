import json
import logging

import aiohttp
import asyncio
from error.errorCode import exceptionLogic, errorLogic
from lib.tokenhelp import tokenhelp

@asyncio.coroutine
def handleHttp(request:dict):
    # 获取玩家简单输赢
    headers=tokenhelp.gen_headers()

    url=tokenhelp.PINBO_URL+'/report/winloss-simple'

    params={}
    params['dateFrom'] = request["end"]#'2018-05-10'
    params['dateTo'] = request["begin"]#'2018-05-19'
    params['userCode']= request["loginId"]

    session = aiohttp.ClientSession()
    try:
        with aiohttp.Timeout(10):
            resp= session.get(url=url, headers=headers, params=params,verify_ssl=False)
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
