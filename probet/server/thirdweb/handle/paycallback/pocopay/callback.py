import asyncio
from lib.jsonhelp import classJsonDump
from lib.timehelp import timeHelp
import logging
import sqlalchemy as sa
import json
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from appweb.logic.paycore import query_to_dict,params_to_query,make_md5_sign
from thirdweb.logic.payresult import processPayResult
from appweb.appweb_config import poco_pay_secret


@asyncio.coroutine
def handleHttp(postData):


    logging.info(postData)
    dictParam = query_to_dict(postData.decode())
    #b'out_trade_no=1527776721461okKwla&trade_no=8060000751180531222521216795&trade_status=SUCCESS&pay_status=1&total_fee=100&rand_str=D2217782948487383C7C9EE893E34B72&timestamp=1527777271&sign=1ea32681d2990c382a66b761a899a5ff'

    payOrderId = dictParam["out_trade_no"]
    trade_status = dictParam["trade_status"]
    total_fee = int(dictParam["total_fee"]) #单位 分
    timestamp = int(dictParam["timestamp"]) #备用数据
    sign = dictParam["sign"]
    #check sign
    dictCheckSign = {}
    for var_key,var_value in dictParam.items():
        if var_key == "sign":
            continue
        if len(var_value)<= 0:
            continue
        try:
            if int(var_value) == 0:
                continue
        except:
            pass

        dictCheckSign[var_key] = var_value

    checkSignParam = params_to_query(dictCheckSign) + "&key={}".format(poco_pay_secret)
    md5Sign = make_md5_sign(checkSignParam)
    if sign != md5Sign:
        logging.error("payOrder [{}] sign check not valid".format(payOrderId))
        return b"Failed"

    if trade_status == "SUCCESS":
        yield from processPayResult(payOrderId,total_fee)
    else:
        logging.error("payOrder [{}] is failed".format(payOrderId))
        return b"Failed"

    return b"SUCCESS"
