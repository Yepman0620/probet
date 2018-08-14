import json
import logging
import aiohttp
from error.errorCode import exceptionLogic, errorLogic
from lib.timehelp.timeHelp import timestamp2Str, getNow
from lib.tokenhelp import tokenhelp
import asyncio

@asyncio.coroutine
def get_wagers(startTime=None,endTime=None,accountId=None):
    # 投注
    # 修改用户状态
    headers = tokenhelp.gen_headers()

    url = tokenhelp.PINBO_URL+'/report/all-wagers'

    data = {}
    if accountId:
        data['userCode'] = "probet."+accountId
    # 时间转换
    if startTime and endTime:
        if endTime-startTime>=24*3600:
            logging.debug(errorLogic.client_param_invalid)
            raise exceptionLogic(errorLogic.client_param_invalid)
        startTime = timestamp2Str(startTime - 12 * 3600)
        endTime = timestamp2Str(endTime - 12 * 3600)
        data['dateFrom'] = startTime  # '2018-05-19 00:00:00'
        data['dateTo'] = endTime  # '2018-05-19 23:40:30'
    data['locale'] = 'zh-cn'

    # 需要校验数据
    session = aiohttp.ClientSession()
    try:
        with aiohttp.Timeout(180):
            resp= yield from session.get(url=url, headers=headers, params=data,verify_ssl=False)
            #print(resp.status)
            if resp.status != 200:
                raise exceptionLogic(errorLogic.client_param_invalid)
    except Exception as e:
        logging.exception(repr(e))
        raise exceptionLogic(errorLogic.sys_unknow_error)
    else:
        res = yield from resp.read()
        res = json.loads(res.decode())
        if type(res) == list:
            pass
        else:
            code = res.get('code', '')
            if code != '' and (code in errorLogic.pinbo_error_code.keys()):
                logging.debug(code + ":" + errorLogic.pinbo_error_code[code])

                raise exceptionLogic([code, errorLogic.pinbo_error_code[code]])
        return res
    finally:
        if session:
            yield from session.close()
