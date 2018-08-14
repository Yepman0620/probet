import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib import certifytoken
from lib.tool import user_token_required
from lib.timehelp import timeHelp


class enumTradeType(object):
    depositType = 1   # 存款
    drawingType = 2   # 取款
    transferType = 3  # 转账
    dividendType = 4  # 红利


class enumTradeStatus(object):
    statusSuccess = 1     # 成功
    statusWait = 2        # 等待
    statusCancel = 3      # 取消
    statusFail = 4        # 失败


class cData():
    def __init__(self):
        self.orderData = []
        self.count = 0


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
    iPage = int(dict_param.get("pageNum",1))
    """
    orderDataList =  yield from classDataBaseMgr.getInstance().getTradeTypeRecord(strAccountId, iTradeType, timeHelp.getNow(), timeHelp.todayStartTimestamp())
    typeDataList = []
    for orderData in orderDataList:
        if iTradeType == orderData.iTradeType:
            typeDataList.append(orderData)
    """
    count = yield from classSqlBaseMgr.getInstance().appGetCoinHisCount(iTradeType, strAccountId)
    listCoinHisIds = yield from classSqlBaseMgr.getInstance().appGetCoinHistory(iTradeType,strAccountId,iPage,10)
    listCoinHisDatas = yield from classDataBaseMgr.getInstance().getCoinHisList(listCoinHisIds)
    listCoinHisData = []
    for CoinHisData in listCoinHisDatas:
        CoinHisData.iCoin = float("%.2f"%round(CoinHisData.iCoin/100,2))
        if CoinHisData.iTradeType == 2:
            CoinHisData.strTransTo = str(CoinHisData.strTransTo)[-4:]
        listCoinHisData.append(CoinHisData)

    # 构造回包
    objRsp.data = cData()
    objRsp.data.orderData = listCoinHisData
    objRsp.data.count = count
    return classJsonDump.dumps(objRsp)






