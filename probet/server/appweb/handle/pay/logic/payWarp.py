import asyncio
from lib.timehelp import timeHelp
from appweb.logic.paycore import params_to_query,make_md5_sign
from appweb.appweb_config import g_PubPem,g_PriPem
from lib.common import sorted_dict
from lib.aiohttpwrap.clientResponse import aiohttpClientResponseWrap
from error.errorCode import errorLogic,exceptionLogic
from appweb.appweb_config import poco_pay_secret
from appweb.logic.paycore import generalPayOrder
import uuid
import rsa
import base64
import aiohttp
import logging
import random
import string
import json


class cData():
    def __init__(self):
        self.payUrl = ""
        self.urlType = 0        #1是返回链接。0是一张二维码图片
        self.codeType = 0       # 0已经生成 直接跳链接，1自己生成
        self.goodsName = ""
        self.goodsPrice = ""
        self.payOrder = ""


@asyncio.coroutine
def lpayPayOrder(strAccountId,iRmbFen,strPayMethord,strIp):

    strPayOrder = str(uuid.uuid1())
    params = {
        "appId": 18412901,
        "merId": "1804121558158584",
        "extInfo": 'probet_lpay',
        "merOrderId": strPayOrder,
        "payerId": 'p.' + strAccountId,
        "notifyUrl": 'http://api.probet.com/paycallback/lpay/callback',
        "reqFee": iRmbFen,  # 请求支付金额，以“分”为单位
        "itemName": "probet充值{}元".format(iRmbFen / 100),  # 商品名称
        "itemDesc": "probet充值{}元".format(iRmbFen / 100),  # 商品描述
    }

    message = params_to_query(params)
    message += "&key={}".format("7DCD4805896049CCADE30A99162E1E8D")
    sign = make_md5_sign(message.encode())
    sign = sign.upper()
    params["signValue"] = sign

    urlType = 0
    codeType = 0
    if strPayMethord == "weixin":
        path = "http://lpay.bhhudong.com/pc/weixin/gateway"
    elif strPayMethord == "alipay":
        path = "http://lpay.bhhudong.com/pc/alipay/gateway"
    elif strPayMethord == "qq":
        path = "http://lpay.bhhudong.com/pc/qqjs/gateway"
    elif strPayMethord == "unionpay_wap":
        path = "http://lpay.bhhudong.com/wap/quick/gateway"
        urlType = 2
    elif strPayMethord == "alipay_wap":
        path = "http://lpay.bhhudong.com/wap/alipay/gateway"
        urlType = 2
    else:
        raise exceptionLogic(errorLogic.pay_channel_not_support)

    respData = cData()
    with aiohttp.Timeout(100):
        try:
            client = aiohttp.ClientSession(response_class=aiohttpClientResponseWrap)
            logging.debug("data center [{}]".format(path))
            # 请求数据中心的接口
            result = yield from client.post(path, data=params)

            if result.status != 200:
                response = yield from result.read()  # 获取返回信息
                logging.error("get status[{}] lapy pay [{}]".format(result.status, response))
            else:
                response = yield from result.read()  # 获取返回信息
                logging.info(response)
                resDict = json.loads(response)

                respData = yield from lPayOrderCall(resDict,strAccountId,strPayOrder,iRmbFen,strPayMethord,strIp,urlType,codeType)

        except Exception as e:
            logging.exception(e)
            raise
        except exceptionLogic as e:
            logging.error(repr(e))
            raise
        finally:
            if client is not None:
                yield from client.close()

    return respData

@asyncio.coroutine
def lPayOrderCall(dictResponse,strAccountId,strPayOrder,iRmbFen,strPayMethord,strIp,urlType,codeType):
    objData = cData()
    if dictResponse["status"] == "OK":

        if urlType == 0:
            objData.payUrl = dictResponse["data"]["codeImgUrl"]
        else:
            objData.payUrl = dictResponse["data"]["payUrl"]

        objData.goodsPrice = int(dictResponse["data"]["reqFee"])
        objData.goodsName = "probet充值{}元".format(iRmbFen / 100)
        # objData.thirdPayOrder = resDict["data"]["orderId"]
        objData.payOrder = strPayOrder
        objData.urlType = urlType
        objData.codeType = codeType

        yield from generalPayOrder(strPayOrder, "","lpay", strAccountId, iRmbFen, strIp, strPayMethord)

    else:
        raise exceptionLogic(errorLogic.pay_failed)

    return objData

@asyncio.coroutine
def pocoPayOrder(strAccountId,iRmbFen,strPayMethord,strChannel,strIp):

    strPayOrder = str(timeHelp.getNowMsec()) + ''.join(random.sample(string.ascii_letters + string.digits, 6))

    params = {
                "merchant_no": "1180412145323712", # 商户号
                "out_trade_no": strPayOrder, # 商户订单号
                "body":"test",
                "pay_type":strPayMethord, # 支付类型
                "trade_amount": str(iRmbFen), # 支付金额，以“分”为单位
                "notify_url": 'http://api.probet.com/paycallback/pocopay/callback',
                "order_desc": 'order_desc', # 商品描述
                "sync_url":"probet.email",
                "client_ip": strIp,#str(dictParam.get("srcIp", "")),
    }

    #print(params)
    #加密post数据
    strJsonPost = json.dumps(params,separators=(',', ':'))

    """
    key = RSA.importKey(RSA_PUBLIC)
    cipher = PKCS1_v1_5.new(key)
    ciphertext = b""
    for var_split_index in range(0,int(len(strJsonPost) / 117) + 1):
        temp = strJsonPost[var_split_index * 117:(var_split_index + 1) * 117]
        ciphertext += cipher.encrypt(temp.encode())
    print(ciphertext)
    """
    retEncrypt = b""

    for var_split_index in range(0,int(len(strJsonPost) / 117) + 1):
        temp = strJsonPost[var_split_index * 117:(var_split_index + 1) * 117]
        retEncrypt += rsa.encrypt(temp.encode(),g_PubPem)

    postData = {"data":base64.b64encode(retEncrypt).decode()}


    path = "http://api.pocopayment.com/v1"
    if strChannel == "wap":
        method = 'com.post.merchant.wap.wapPay.create'
    elif strChannel == "scan":
        method = 'com.post.merchant.pay.directPay.trade'
    elif strChannel == "quick":
        method = 'com.post.merchant.quick.Order.OrderPayInit'
    else:
        raise exceptionLogic(errorLogic.pay_type_not_valid)

    getParam = {
      "method":method,
      "pid": "10802751000000610618",
      "timestamp": str(timeHelp.getNow()),
      "randstr": make_md5_sign(str(uuid.uuid4()).encode()),
    }


    totalSignParam = {"data":params}
    totalSignParam.update(getParam)
    messageDict = sorted_dict(totalSignParam)
    message = json.dumps(messageDict,separators=(',', ':')) + poco_pay_secret
    #message = message.replace(" ","")
    sign = make_md5_sign(message.encode())
    getParam["sign"] = sign

    getUrl = params_to_query(getParam)

    respData = cData()
    with aiohttp.Timeout(100):
        try:
            client = aiohttp.ClientSession(response_class=aiohttpClientResponseWrap)
            logging.debug("data center [{}]".format(path))
            # 请求数据中心的接口
            logging.info(path + "?" + getUrl)
            logging.info(postData)

            result = yield from client.post(path + "?" + getUrl, data=postData)
            if result.status != 200:
                response = yield from result.read()  # 获取返回信息
                logging.error("get status[{}] qqpay [{}]".format(result.status,response))
            else:
                response = yield from result.read()  # 获取返回信息
                b64DecodeResp = base64.b64decode(response)
                responseDecrypt = b""
                for var_decode_split in range(0,int(len(b64DecodeResp)/128)):
                    temp = b64DecodeResp[var_decode_split * 128:(var_decode_split + 1) * 128]
                    responseDecrypt += rsa.decrypt(temp,g_PriPem)
                logging.info(responseDecrypt)

                dictResponse = json.loads(responseDecrypt)
                respData = yield from pocoWrapPayOrderCall(dictResponse,strAccountId,strPayOrder,iRmbFen,strPayMethord,strIp)

        except Exception as e:
            logging.exception(e)
            raise
        except exceptionLogic as e:
            logging.error(repr(e))
            raise
        finally:
            if client is not None:
                yield from client.close()

    return respData

@asyncio.coroutine
def pocoWrapPayOrderCall(dictResponse,strAccountId,strPayOrder,iRmbFen,strPayMethord,strIp):
    objData = cData()
    if int(dictResponse["errcode"]) == 0:
        if dictResponse["data"]["result_code"] == "0":


            objData.payUrl = dictResponse["data"]["out_pay_url"]
            objData.goodsPrice = iRmbFen
            objData.goodsName = "probet充值{}元".format(iRmbFen / 100)
            objData.payOrder = strPayOrder
            objData.urlType = 0

            yield from generalPayOrder(strPayOrder,"","poco",strAccountId,iRmbFen,strIp,strPayMethord)

            return objData
        else:
            raise exceptionLogic(errorLogic.pay_failed)
    else:
        raise exceptionLogic(errorLogic.pay_failed)


@asyncio.coroutine
def XgxPayOrder(strAccountId,iRmbFen,strPayMethord,strChannel,strIp):


    params = {
        "merchant_id": "",
        "merId": "1804121558158584",
        "extInfo": 'test',
        "merOrderId": strPayOrder,
        "payerId": 'p' + timeHelp.timestamp2Str(timeHelp.getNow()),
        "notifyUrl": 'http://api.probet.com/paycallback/lpay/callback',
        "reqFee": iRmbFen,  # 请求支付金额，以“分”为单位
        "itemName": "probet充值{}元".format(iRmbFen / 100),  # 商品名称
        "itemDesc": "probet充值{}元".format(iRmbFen / 100),  # 商品描述
    }