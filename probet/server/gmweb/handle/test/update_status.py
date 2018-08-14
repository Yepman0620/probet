import json
import logging

import aiohttp
import asyncio
from error.errorCode import exceptionLogic, errorLogic
from lib.tokenhelp import tokenhelp

@asyncio.coroutine
def handleHttp(request:dict):
    # 修改用户状态
    headers=tokenhelp.gen_headers()

    url=tokenhelp.PINBO_URL+'/player/update-status'

    data={}
    data['userCode']='PSZ4000002'
    data['status']='ACTIVE'
    # 需要校验数据

    session = aiohttp.ClientSession()
    try:
        with aiohttp.Timeout(10):
            resp= session.post(url=url,headers=headers,data=data,verify_ssl=False)
            if resp.status!=200:
                raise exceptionLogic(errorLogic.client_param_invalid)

    except Exception as e:
        logging.exception(e)
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