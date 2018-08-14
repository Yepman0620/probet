import json
import logging
import time
import asyncio
import aiohttp

from error.errorCode import errorLogic, exceptionLogic
from lib.tokenhelp import tokenhelp
from lib.constants import shaba_url

@asyncio.coroutine
def handleHttp(request:dict):
    # 注册sb
    url=shaba_url+'/CreateMember'
    params={}
    params['vendor_id']='1234'
    params['vendor_member_id']='1234'
    params['operatorid']='1234'
    params['firstname']='1234'
    params['lastname']='1234'
    params['username']='1234'
    params['oddstype']=1
    params['currency']=20
    params['maxtransfer']=100
    params['mintransfer']=10

    # 需要校验数据
    session= aiohttp.ClientSession()
    try:
        with aiohttp.Timeout(10):
            resp=yield from session.post(url=url, params=params,verify_ssl=False)
            print(resp.text)
            print(resp.status)
            if resp.status != 200:
                raise exceptionLogic(errorLogic.client_param_invalid)

    except Exception as e:
        logging.debug(repr(e))
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
