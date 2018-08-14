import asyncio
from appweb.logic.paycore import query_to_dict,params_to_query,make_md5_sign
from thirdweb.logic.payresult import processPayResult
import logging

@asyncio.coroutine
def handleHttp(postData: bytes):

    """
    amount=200&orderTime=20180804151557&orderId=L20180804151538158062&appId=18412901&orderStatus=0&merId=1804121558158584&signValue=5F6FF97CA9C6E59D1BC5A7F3EF65863A&merOrderId=30053b98-97b6-11e8-844f-00163ca64285&extInfo=test
    """
    #todo bill
    logging.info(postData)
    #这个支付已经停了
    dictParam = query_to_dict(postData.decode())

    payOrderId = dictParam["merOrderId"]
    merId = dictParam["merId"]
    trade_status = dictParam["orderStatus"]
    amount = int(dictParam["amount"])  # 单位 分
    orderTime = int(dictParam["orderTime"])  # 备用数据
    signValue = dictParam["signValue"]

    if str(merId) != "1804121558158584":
        return b'fail'

    dictCheckSign = {}
    for var_key, var_value in dictParam.items():
        if var_key == "signValue":
            continue
        if len(var_value) <= 0:
            continue
        try:
            if int(var_value) == 0:
                continue
        except:
            pass

        dictCheckSign[var_key] = var_value

    checkSignParam = params_to_query(dictCheckSign) + "&key=7DCD4805896049CCADE30A99162E1E8D"

    md5Sign = make_md5_sign(checkSignParam)
    if signValue != md5Sign.upper():
        logging.error("payOrder [{}] sign check not valid".format(payOrderId))
        #TODO modify the sign
        if int(trade_status) == 0:
            ret = yield from processPayResult(payOrderId, amount)
        else:
            return b"fail"
    else:
        if int(trade_status) == 0:
            ret = yield from processPayResult(payOrderId,amount)
        else:
            logging.error("payOrder [{}] is failed".format(payOrderId))
            return b"fail"

    if ret != 0:
        return b"fail"
    else:
        return b"success"


if __name__ == "__main__":
    #todo bill
    #这个支付已经停了
    postData = b'amount=200&orderTime=20180804151557&orderId=L20180804151538158062&appId=18412901&orderStatus=0&merId=1804121558158584&signValue=5F6FF97CA9C6E59D1BC5A7F3EF65863A&merOrderId=30053b98-97b6-11e8-844f-00163ca64285&extInfo=test'
    dictParam = query_to_dict(postData.decode())
    payOrderId = dictParam["merOrderId"]
    merId = dictParam["merId"]
    trade_status = dictParam["orderStatus"]
    amount = int(dictParam["amount"])  # 单位 分
    orderTime = int(dictParam["orderTime"])  # 备用数据
    signValue = dictParam["signValue"]

    if str(merId) != "1804121558158584":
        print('fail')

    dictCheckSign = {}
    for var_key, var_value in dictParam.items():
        if var_key == "signValue":
            continue
        if len(var_value) <= 0:
            continue
        try:
            if int(var_value) == 0:
                continue
        except:
            pass

        dictCheckSign[var_key] = var_value

    checkSignParam = params_to_query(dictCheckSign) + "&key=7DCD4805896049CCADE30A99162E1E8D"

    md5Sign = make_md5_sign(checkSignParam)
    if signValue != md5Sign.upper():
        print('fail')
