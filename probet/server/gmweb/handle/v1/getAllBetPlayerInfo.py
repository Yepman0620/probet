import asyncio
from gmweb.protocol import gmProtocol
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.jsonhelp import classJsonDump

@asyncio.coroutine
def handleHttp(dict_param:dict):

    strGuessId = dict_param['strGuessId']
    iPage = dict_param["iPage"]
    iNum = dict_param["iNum"]

    iBeginIndex = iPage * iNum
    iEndIndex = iBeginIndex + iNum

    objResp = gmProtocol.classGmAllPlayerData()
    objGuessData = yield from classDataBaseMgr.getInstance().getGuessDataByLock(strGuessId)
    objResp.arrChooseName = list(objGuessData.dictCTR.keys())
    objResp.iTotal  = yield from classDataBaseMgr.getInstance().getCurrentGuessMemberLen(strGuessId)
    listCurrent = yield from classDataBaseMgr.getInstance().getCurrentGuessMember(strGuessId,iBeginIndex, iEndIndex)

    if len(listCurrent) > 0:

        for var_member in listCurrent:
            objNewData = gmProtocol.classGmRecentBetItem()
            objNewData.strAccountId = var_member["id"]
            objNewData.strChooseId = var_member["type"]
            objNewData.iBetNum = var_member["num"]
            objResp.arrCurrentBetInfo.append(objNewData)

    return classJsonDump.dumps(objResp)

