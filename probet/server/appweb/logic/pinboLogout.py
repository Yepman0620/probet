import json
import logging

import aiohttp
import asyncio
from error.errorCode import exceptionLogic, errorLogic
from lib.tokenhelp import tokenhelp
from appweb.proc import procVariable

@asyncio.coroutine
def loginout_pinbo(accountId):
    url = "/player/logout"
    data = {}
    data['userCode'] = 'probet.' + accountId
    headers = tokenhelp.gen_headers()

    if procVariable.debug:
        headers["refer"] = "probet"

    session = aiohttp.ClientSession()
    try:
        with aiohttp.Timeout(10):
            resp = yield from session.post(tokenhelp.PINBO_URL + url, headers=headers, data=data,verify_ssl=False)
            if resp.status != 200:
                logging.error("{}|{}".format(errorLogic.third_party_error[1],data))
                raise exceptionLogic(errorLogic.third_party_error)

    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.sys_unknow_error)
    else:
        res = yield from resp.read()
        resp = json.loads(res.decode())

    finally:
        if session is not None:
            yield from session.close()

    return resp