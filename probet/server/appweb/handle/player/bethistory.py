import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib.tool import user_token_required


class enumGetBetHistoryType(object):
    getType1 = 0      #获取1天之内的
    getType3 = 1      #获取3天之内的
    getType7 = 2     #获取7天内的
    getType30 = 3     #获取1个月内的


class cData():
    def __init__(self):
        self.productName = ""
        self.totalCount = 0
        self.betWaterCoin = 0
        self.winRate = 0.0
        self.winCoin = 0

class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = []


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):

    objRsp = cResp()
    try:
        strAccountId = dict_param["accountId"]
        #strToken = dict_param["token"]
        iTimeRangeType = int(dict_param["timerangetype"])

    except Exception as e:
        raise exceptionLogic(errorLogic.client_param_invalid)
    """
    if strToken is None:
        raise exceptionLogic(errorLogic.login_token_not_valid)

    ret = certifytoken.certify_token(strAccountId, strToken)
    if ret != True:
        raise exceptionLogic(errorLogic.login_token_expired)
    """
    if iTimeRangeType == enumGetBetHistoryType.getType1:
        iDayRange = 1
    elif iTimeRangeType == enumGetBetHistoryType.getType3:
        iDayRange = 3
    elif iTimeRangeType == enumGetBetHistoryType.getType7:
        iDayRange = 7
    elif iTimeRangeType == enumGetBetHistoryType.getType30:
        iDayRange = 30
    else:
        raise exceptionLogic(errorLogic.login_token_not_valid)

    #自己盘口的统计信息
    retDict = yield from classSqlBaseMgr.getInstance().getBetHistoryAllWaterWinSum(iDayRange,strAccountId)
    # 构造回包
    objDjResp = cData()
    objDjResp.productName = "电竞竞猜"
    objDjResp.totalCount = retDict["total"]
    objDjResp.betWaterCoin = retDict["waterCoin"]/100
    objDjResp.winCoin = retDict["winCoin"]/100
    if objDjResp.totalCount != 0:
        objDjResp.winRate = '{}%'.format(round(retDict["winCount"] / objDjResp.totalCount,2) * 100)
    else:
        objDjResp.winRate = '0.0%'
    objRsp.data.append(objDjResp)


    #平博盘口的统计信息
    retDict = yield from classSqlBaseMgr.getInstance().getPinboHistoryAllWaterWinSum(iDayRange, strAccountId)
    objDjResp = cData()
    objDjResp.productName = "平博竞猜"
    objDjResp.totalCount = retDict["total"]
    #TODO 跟前端确认一下，平博的是不是前端/100了
    objDjResp.betWaterCoin = retDict["waterCoin"]
    objDjResp.winCoin = retDict["winCoin"]
    if objDjResp.totalCount != 0:
        if not retDict['settleCount']:
            objDjResp.winRate = '0.0%'
        objDjResp.winRate = '{}%'.format(round(retDict["winCount"] / retDict["settleCount"], 2) * 100)
    else:
        objDjResp.winRate = '0.0%'
    objRsp.data.append(objDjResp)

    return classJsonDump.dumps(objRsp)

