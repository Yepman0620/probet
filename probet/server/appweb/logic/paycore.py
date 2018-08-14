import hashlib
import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
from logic.data.userData import classPayData
from lib.timehelp import timeHelp
from logic.enum.enumCoinOp import CoinOp
from datawrapper.playerDataOpWrapper import addPlayerBill
from error.errorCode import errorLogic,exceptionLogic
import uuid
import logging

def make_md5_sign(message):
    if type(message) is str:
        message = message.encode()

    m = hashlib.md5()
    m.update(message)
    #m.update(server_config.key)
    return m.hexdigest()


def query_to_dict(query):
    """
    将query string转换成字典
    :param query:
    :return:
    """
    res = {}
    k_v_pairs = query.split("&")
    for item in k_v_pairs:
        sp_item = item.split("=", 1)  #注意这里，因为sign秘钥里面肯那个包含'='符号，所以splint一次就可以了
        key = sp_item[0]
        value = sp_item[1]
        res[key] = value

    return res

def params_to_query(params, quotes=False, reverse=False):
    """
        生成需要签名的字符串
    :param params:
    :return:
    """
    """
    :param params:
    :return:
    """
    query = ""
    for key in sorted(params.keys(), reverse=reverse):
        value = params[key]
        if quotes == True:
            query += str(key) + "=\"" + str(value) + "\"&"
        else:
            query += str(key) + "=" + str(value) + "&"
    query = query[0:-1]
    return query


@asyncio.coroutine
def generalPayOrder(strPayOrder,strThirdOrder,strThirdPayName,strAccountId,iRmbFen,srcIp,payChannel,bank=""):

    objNewPayOrder = classPayData()
    objNewPayOrder.strPayOrder = strPayOrder
    objNewPayOrder.strThirdPayOrder = strThirdOrder#dictResponse["data"]["order_sn"]
    objNewPayOrder.strThirdPayName = strThirdPayName
    objNewPayOrder.strAccountId = strAccountId
    objNewPayOrder.iBuyCoin = iRmbFen
    objNewPayOrder.iOrderTime = timeHelp.getNow()
    objNewPayOrder.strIp = srcIp#str(dictParam.get("srcIp", ""))
    objNewPayOrder.strPayChannel = payChannel
    objNewPayOrder.strBank = bank

    yield from classDataBaseMgr.getInstance().setPayOrderByLock(objNewPayOrder, save=False,
                                                                new=True)
    objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(strAccountId)
    if objPlayerData is None:
        logging.error("player data is None [{}]".format(strAccountId))
        raise exceptionLogic(errorLogic.player_data_not_found)
    
    #iBalance = objPlayerData.iCoin + iRmbFen
    yield from addPlayerBill(strAccountId=strAccountId,iOpCoin=iRmbFen,iBalance=objPlayerData.iCoin,enumOp=CoinOp.coinOpPay,tradeState=2,transFrom=payChannel,transTo=bank,
                             srcIp=srcIp,strOrderId=strPayOrder)