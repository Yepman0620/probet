import json
import logging
import time
import aiohttp
import requests
from error.errorCode import exceptionLogic, errorLogic
from lib.tokenhelp import tokenhelp
import asyncio

@asyncio.coroutine
def handleHttp(request:dict):
    # 投注
    # 修改用户状态
    headers = tokenhelp.gen_headers()

    url = tokenhelp.PINBO_URL+'/report/wagers'

    data = {}
    data['userCode'] = 'PSZ4000002'
    data['locale'] = 'zh-cn'
    data['dateFrom']='2018-05-19 00:00:00'
    data['dateTo']='2018-05-19 23:40:30'
    data['product']='SB'
    data['settle']=True
    data['filterBy']='event_date'

    resp=requests.get(url=url,headers=headers,params=data)
    print(resp.content)

    # 需要校验数据
    session = aiohttp.ClientSession()
    try:
        with aiohttp.Timeout(10):
            resp= session.get(url=url, headers=headers, params=data,verify_ssl=False)
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
