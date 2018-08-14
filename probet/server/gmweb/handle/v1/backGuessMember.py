import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
from ssprotocol import dataHeaderDefine
from ssprotocol.protoDataCenterResult import result_msgId,BackReq
from error.errorCode import errorLogic,exceptionLogic
from lib.pubSub.pubMgr import classPubMgr


@asyncio.coroutine
def handleHttp(dict_param: dict):

    strMarchId = dict_param['strMatchId']
    strGuessId = dict_param['strGuessId']

    msgHead = dataHeaderDefine.classResultHead()
    msgHead.strMsgId = result_msgId.msg_back
    msgBody = BackReq()
    msgBody.strMatchId = strMarchId
    msgBody.strGuessId = strGuessId

    objGuessData = yield from classDataBaseMgr.getInstance().getGuessDataByLock(strGuessId)
    if objGuessData is None:
        raise exceptionLogic(errorLogic.guess_data_not_found)

    for var_key,var_value in objGuessData.dictCTR.items():
        yield from classDataBaseMgr.getInstance().resetResultRedisList(strGuessId,var_value.strId)

    yield from classPubMgr.getInstance("resultPub").publish(msgHead,msgBody)
