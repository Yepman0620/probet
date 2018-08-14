import json
import logging

import aiohttp
import asyncio
from error.errorCode import errorLogic, exceptionLogic
from lib.tokenhelp import tokenhelp

@asyncio.coroutine
def deposit(kind,accountId,amount):

    headers=tokenhelp.gen_headers()
    if kind not in ['deposit','withdraw']:
        raise exceptionLogic(errorLogic.client_param_invalid)

    # 用户存款
    if kind=='deposit':
        url=tokenhelp.PINBO_URL+'/player/deposit'
    else:
        # 用户提款
        url = tokenhelp.PINBO_URL+'/player/withdraw'
    data={}
    data['userCode']='probet.'+accountId
    data['amount']=amount
    if amount <=0:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    session= aiohttp.ClientSession()
    try:
        with aiohttp.Timeout(10):
            print(data)
            resp= yield from session.post(url=url,headers=headers,data=data,verify_ssl=False)
            if resp.status!=200:
                logging.debug(errorLogic.client_param_invalid)
                return 4

    except Exception as e:
        logging.debug(e)
        return 4

    else:
        res=yield from resp.read()
        res = json.loads(res.decode())
        print(res)
        code = res.get('code', '')
        if code != '' and (code in errorLogic.pinbo_error_code.keys()):
            logging.debug(code+":"+errorLogic.pinbo_error_code[code])

            return 4

        return 1

    finally:
        if session:
            yield from session.close()
