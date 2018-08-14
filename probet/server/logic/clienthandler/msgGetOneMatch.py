from ssprotocol.dataHeaderDefine import classSSHead
from datawrapper.dataBaseMgr import classDataBaseMgr
from csprotocol.protoMatch import enumGetMatchType
from error.errorCode import exceptionLogic,errorLogic
from csprotocol.protoMatch import protoGetOneMatchResp,protoMatchItem
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from logic.logicmgr import checkParamValid as cpv
import asyncio


@asyncio.coroutine
def handleGetOneMatch(objHead:classSSHead,objFbReq:dict):

    strMatchId = objFbReq.get("strMatchId")

    if not cpv.checkIsString(strMatchId):
        raise exceptionLogic(errorLogic.client_param_invalid)


    var_matchData = yield from classDataBaseMgr.getInstance().getMatchData(strMatchId)
    # 统一一批拿出guess数据
    dictGuessDatas = yield from classDataBaseMgr.getInstance().getGuessDataListRetDict(var_matchData.arrayGuess)

    objResp = protoGetOneMatchResp()
    objMatchItem = protoMatchItem(var_matchData)
    for var_round,var_list in var_matchData.dictGuess.items():
        for var_guess_id in var_list:
            objGuessData = dictGuessDatas.get(var_guess_id)
            if objGuessData is not None:
                objMatchItem.buildRoundGuess(var_round,objGuessData)

    objResp.listMatchList.append(objMatchItem)

    return objResp
