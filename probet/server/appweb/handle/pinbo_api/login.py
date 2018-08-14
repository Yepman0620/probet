import json
import logging

import aiohttp
import asyncio
from error.errorCode import exceptionLogic, errorLogic
from lib.tokenhelp import tokenhelp

@asyncio.coroutine
def handleHttp(request:dict):
    """对接pinbo登陆接口
    """
    headers=tokenhelp.gen_headers()
    accountId=request.get("accountId")
    token=request.get("token")

    if not accountId:
        raise exceptionLogic(errorLogic.client_param_invalid)
    # userCode= 获取userCode通过user_id
    url = "/player/login"

    data={}
    data['userCode']='probet.'+accountId
    data['locale']='zh-cn'

    try:
        with aiohttp.ClientSession() as session:
            with aiohttp.Timeout(10):
                 with (yield from session.post(tokenhelp.PINBO_URL+url,headers=headers,data=data,verify_ssl=False)) as resp:
                    if resp.status !=200:
                        raise exceptionLogic(errorLogic.client_param_invalid)

    except Exception as e :
        logging.error(e)
        raise exceptionLogic(errorLogic.sys_unknow_error)
    else:
        res = yield from resp.read()
        res = json.loads(res.decode())
        code = res.get('code', '')
        if code != '' and (code in errorLogic.pinbo_error_code.keys()):
            logging.exception(code + ":" + errorLogic.pinbo_error_code[code])
            raise exceptionLogic([code, errorLogic.pinbo_error_code[code]])

        res=json.loads(res)
        login_url=res.get('loginUrl')
        return login_url




