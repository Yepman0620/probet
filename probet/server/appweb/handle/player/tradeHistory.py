import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib import certifytoken
from lib.timehelp import timeHelp
from lib.tool import user_token_required


class enumTradeType(object):
    depositType = 1   # 存款
    drawingType = 2   # 取款
    transferType = 3  # 转账
    dividendType = 4  # 红利



class enumGetTradeHistoryType(object):
    getType1 = 1  # 获取1天之内的
    getType3 = 2  # 获取3天之内的
    getType7 = 3  # 获取7天内的
    getType30 = 4  # 获取1个月内的

class enumTradeStatus(object):
    statusSuccess = 1     # 成功
    statusWait = 2        # 等待
    statusCancel = 3      # 取消
    statusFail = 4        # 失败


class cData():
    def __init__(self):
        self.orderData = []


class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """交易记录"""
    objRsp = cResp()

    strAccountId = dict_param.get("accountId", "")
    iTradeType = dict_param.get("tradeType", "")
    iDateType = dict_param.get("dateType", "")
    iPage = int(dict_param.get("pageNum",1))

    if not all([iTradeType, iDateType]):
        raise exceptionLogic(errorLogic.client_param_invalid)

    if iDateType ==enumGetTradeHistoryType.getType1:
        """
        orderDataList =  yield from classDataBaseMgr.getInstance().getTradeTypeRecord(strAccountId, iTradeType, timeHelp.getNow(), timeHelp.todayStartTimestamp())
        typeDataList = []
        for orderData in orderDataList:
            if iTradeType == orderData.iTradeType:
                typeDataList.append(orderData)
        """
        listCoinHisIds = yield from classSqlBaseMgr.getInstance().getCoinHistory(timeHelp.todayStartTimestamp(),iTradeType,strAccountId,iPage,7)
        listCoinHisDatas = yield from classDataBaseMgr.getInstance().getCoinHisList(listCoinHisIds)


    elif iDateType == enumGetTradeHistoryType.getType3:
        listCoinHisIds = yield from classSqlBaseMgr.getInstance().getCoinHistory(timeHelp.threeDayTimestamp(),
                                                                                 iTradeType, strAccountId, iPage, 7)
        listCoinHisDatas = yield from classDataBaseMgr.getInstance().getCoinHisList(listCoinHisIds)

    elif iDateType == enumGetTradeHistoryType.getType7:
        listCoinHisIds = yield from classSqlBaseMgr.getInstance().getCoinHistory(timeHelp.sevenDayTimestamp(),
                                                                                 iTradeType, strAccountId, iPage, 7)
        listCoinHisDatas = yield from classDataBaseMgr.getInstance().getCoinHisList(listCoinHisIds)
    else:
        listCoinHisIds = yield from classSqlBaseMgr.getInstance().getCoinHistory(timeHelp.thirtyDayTimestamp(),
                                                                                 iTradeType, strAccountId, iPage, 7)
        listCoinHisDatas = yield from classDataBaseMgr.getInstance().getCoinHisList(listCoinHisIds)

    listCoinHisData = []
    for CoinHisData in listCoinHisDatas:
        CoinHisData.iCoin = float("%.2f" % round(CoinHisData.iCoin / 100, 2))
        listCoinHisData.append(CoinHisData)
    # 构造回包
    objRsp.data = cData()
    objRsp.data.orderData = listCoinHisData

    return classJsonDump.dumps(objRsp)























