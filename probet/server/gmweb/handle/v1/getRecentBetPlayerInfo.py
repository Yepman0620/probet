import asyncio
from gmweb.protocol import gmProtocol
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.jsonhelp import classJsonDump

@asyncio.coroutine
def handleHttp(dict_param:dict):

    strGuessId = dict_param['strGuessId']
    iCursor = int(dict_param['iCursor'])
    iLen = yield from classDataBaseMgr.getInstance().getCurrentGuessMemberLen(strGuessId)
    if iLen > 15:
        iCursor = iLen - 15

    listCurrent = yield from classDataBaseMgr.getInstance().getCurrentGuessMember(strGuessId, iCursor,iLen)
    objResp = gmProtocol.classGmRecentPlayerData()
    objResp.iCursor = iLen
    if len(listCurrent) > 0:
        objGuessData = yield from classDataBaseMgr.getInstance().getGuessData(strGuessId)

        objResp.arrChooseName = list(objGuessData.dictCTR.keys())
        for var_member in listCurrent:
            objNewData = gmProtocol.classGmRecentBetItem()
            objNewData.strAccountId = var_member["id"]
            objNewData.strChooseId = var_member["type"]
            objNewData.iBetNum = var_member["num"]
            objResp.arrCurrentBetInfo.append(objNewData)
    #print(classJsonDump.dumps(objResp))
    return classJsonDump.dumps(objResp)

