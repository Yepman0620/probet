import asyncio
import logging
import json
import aiohttp
from error.errorCode import errorLogic
from lib.timehelp.timeHelp import timestamp2Str, getNow
from lib.tokenhelp import tokenhelp

@asyncio.coroutine
def get_settle_wagers(session):
    headers = tokenhelp.gen_headers()
    url = tokenhelp.PINBO_URL+'/report/all-wagers'

    data = {}
    data['settle']=1
    data['locale'] = 'zh-cn'
    startTime = timestamp2Str(getNow() - 17 * 3600)
    endTime = timestamp2Str(getNow() - 12 * 3600)
    data['dateFrom'] = startTime  # '2018-05-19 00:00:00'
    data['dateTo'] = endTime  # '2018-05-19 23:40:30'

    # 需要校验数据

    try:
        with aiohttp.Timeout(180):
            resp= yield from session.get(url=url, headers=headers, params=data,verify_ssl=False,timeout=180)
            if resp.status != 200:
                logging.exception('pingbo network error [{}]'.format(resp))
                return []
    except Exception as e:
        logging.exception(repr(e))
        return []
    else:
        res = yield from resp.read()
        res = json.loads(res.decode())
        if isinstance(res,list):
            return res
        else:
            code = res.get('code', '')
            if code != '' and (code in errorLogic.pinbo_error_code.keys()):
                logging.exception(code + ":" + errorLogic.pinbo_error_code[code])
                return []


