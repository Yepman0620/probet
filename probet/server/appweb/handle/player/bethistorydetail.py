import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
import json
from lib.tool import user_token_required


class enumGetBetHistoryType(object):
    getType1 = 0  # 获取1天之内的
    getType3 = 1  # 获取3天之内的
    getType7 = 2  # 获取7天内的
    getType30 = 3  # 获取1个月内的

class enumBetState(object):
    stateNone = 0     #未结算
    stateWin = 1      #赢
    statelost = 2     #输
    stateCancel = 3   #取消
    stateStart = 4    #即将开始
    stateDelete = 5   #已删除


class cData():
    def __init__(self):
        self.timestamp = 0
        self.gameType = ""
        self.orderId = ""
        self.orderDes = ""
        self.betRate = 0
        self.betCoin = 0
        self.betWin = 0  #输赢金额
        self.state = 0

class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = []
        self.total = 0


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):

    objRsp = cResp()
    strAccountId = dict_param.get("accountId","")
    iTimeRangeType = int(dict_param.get("timerangetype",0))
    iPageNum = dict_param.get("pagenum",1)
    #iPageSize = int(dict_param["pageSize"])
    strBillType = dict_param.get("billType","")
    if not iPageNum:
        raise exceptionLogic(errorLogic.client_param_invalid)

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

    if iPageNum <= 0:
        raise exceptionLogic(errorLogic.login_token_not_valid)

    if strBillType == "probet" or strBillType == "":

        objRsp.total = yield from classSqlBaseMgr.getInstance().getBetHistoryAllNum(iDayRange, strAccountId)
        retListIds = yield from classSqlBaseMgr.getInstance().getBetHistoryDetail(iDayRange, strAccountId,iPageNum,10)
        retListDatas = yield from classDataBaseMgr.getInstance().getBetHistoryList(retListIds)

        # 构造回包
        for var in retListDatas:
            objData = cData()
            objData.timestamp = var.iTime#timeHelp.timestamp2Str(var.iTime)
            objData.gameType = var.strMatchType
            objData.orderId = var.strGuessUId
            objData.orderDes = "{} | {}".format(var.strGuessName,var.dictCTR[var.strChooseId].strChooseName)
            objData.betRate = var.dictCTR[var.strChooseId].fRate
            objData.betCoin = var.iBetCoin/100
            objData.betWin = (var.iWinCoin-var.iBetCoin)/100  # 输赢金额
            if var.iResult < 4:
                objData.state = 0
            elif (var.iResult == 5 or var.iResult == 6 or var.iResult == 7 or var.iResult == 8) and objData.betWin <= 0:
                objData.state = 3
            elif objData.betWin > 0:
                objData.state = 1
            elif objData.betWin <= 0:
                objData.state = 2
            objRsp.data.append(objData)

    elif strBillType == "pingbo":
        objRsp.total = yield from classSqlBaseMgr.getInstance().getPinBoBetHistoryAllNum(iDayRange, strAccountId)
        retListDatas = yield from classSqlBaseMgr.getInstance().getPinBoBetHistoryDetail(iDayRange, strAccountId, iPageNum, 10)
        #retListDatas = yield from classDataBaseMgr.getInstance().getPinBoBetHistoryList(retListIds)

        # 构造回包
        for var in retListDatas:
            objData = cData()
            dictMessageData = json.loads(json.loads(var.messageData))
            objData.timestamp = var.wagerDateFm  # timeHelp.timestamp2Str(var.iTime)
            objData.gameType = dictMessageData["sport"]
            objData.orderId = var.wagerId
            objData.orderDes = "{} | {}".format(dictMessageData["league"], dictMessageData["selection"])
            objData.betRate = var.odds
            objData.betCoin = var.toRisk
            objData.betWin = var.winLoss  # 输赢金额
            if var.status == "PENDING":
                objData.state = 0
            elif var.status == "OPEN":
                objData.state = 4
            elif var.status == "CANCELLED":
                objData.state = 3
            elif var.status == "DELETED":
                objData.state = 5
            elif objData.betWin > 0:
                objData.state = 2
            elif objData.betWin < 0:
                objData.state = 1
            objRsp.data.append(objData)

    return classJsonDump.dumps(objRsp)

