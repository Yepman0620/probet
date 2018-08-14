import asyncio
from logic.data import matchData
from error.errorCode import exceptionLogic,errorLogic
from datawrapper.dataBaseMgr import classDataBaseMgr
import uuid
from lib.common import sorted_dict

@asyncio.coroutine
def handleHttp(dict_param:dict):
    strMatchId = dict_param['strMatchId']
    iMatchIndex = int(dict_param['iMatchIndex'])  # 第几局
    dictPlayInfo = dict_param['dictPlayInfo']
    #strPlayId = dictPlayInfo['strPlayId']         # 玩法id,同名字
    strPlayName = dictPlayInfo['strPlayName']     # 玩法名称：一血


    objMatch,objMatchLock = yield from classDataBaseMgr.getInstance().getMatchDataByLock(strMatchId)
    if objMatch is None:
        raise exceptionLogic(errorLogic.match_data_not_found)

    objGuess = matchData.classGuessData()
    objGuess.strGuessId = str(uuid.uuid4())#objMatch.strMatchId + "_guessId_{}_{}".format(iMatchIndex, strPlayId)
    objGuess.strGuessName = strPlayName
    objGuess.iGuessState = 0
    objGuess.strOwnerMatchId = strMatchId

    if objGuess.strGuessId not in objMatch.arrayGuess:
        objMatch.arrayGuess.append(objGuess.strGuessId)

    listRoundGuess = objMatch.dictGuess.get(iMatchIndex, None)
    if listRoundGuess is None:
        objMatch.dictGuess[iMatchIndex] = []
        objMatch.dictGuess[iMatchIndex].append(objGuess.strGuessId)
    else:
        listRoundGuess.append(objGuess.strGuessId)

    # 先初始化
    for choose_item in dictPlayInfo['arrayChooseItem']:
        objNew = matchData.CTR()
        objNew.strId = str(uuid.uuid4())#choose_item['strDictKey'].strip()
        objNew.strChooseName = choose_item['strDictName'].strip()
        objNew.fRate = float("%.2f"%round(float(choose_item["strOdd"]),2))
        if objNew.fRate <= 1.0:
            yield from classDataBaseMgr.getInstance().releaseMatchLock(strMatchId,objMatchLock)
            raise exceptionLogic(errorLogic.guessInitRate_Less1Value)

        objGuess.dictCTR[objNew.strId] = objNew

    yield from classDataBaseMgr.getInstance().addGuessData(objGuess)

    #排序一下,按照轮次
    objMatch.dictGuess = sorted_dict(objMatch.dictGuess)
    yield from classDataBaseMgr.getInstance().setMatchDataByLock(objMatch,objMatchLock)
