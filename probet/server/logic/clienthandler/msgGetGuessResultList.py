from ssprotocol.dataHeaderDefine import classSSHead
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic,errorLogic
from csprotocol.protoMatch import protoGetGuessResultListResp,protoGuessHistoryItem
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from logic.logicmgr import checkParamValid as cpv
import asyncio


@asyncio.coroutine
def handleGetGuessResultList(objHead:classSSHead,objFbReq:dict):
    objResp = protoGetGuessResultListResp()
    strAccount = objHead.strAccountId
    if strAccount == "":
        return objResp

    if not cpv.checkIsString(strAccount):
        raise exceptionLogic(errorLogic.client_param_invalid)

    listGuessUIds = yield from classSqlBaseMgr.getInstance().getGuessResultHistory(strAccount)
    # 统一一批拿出guess数据
    listBetHistoryData = yield from classDataBaseMgr.getInstance().getBetHistoryList(listGuessUIds)

    for var_history in listBetHistoryData:
        objBetHistoryItem = protoGuessHistoryItem(var_history)
        objResp.listGuessResultList.append(objBetHistoryItem)

    return objResp
