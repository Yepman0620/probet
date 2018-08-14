import asyncio
import json
import aiohttp
import random
from lib.aiohttpwrap.clientResponse import aiohttpClientResponseWrap
from lib.timehelp import timeHelp
from datawrapper.dataBaseMgr import classDataBaseMgr
import logging
from logic.data import matchData
from matchcenter import matchcenter_config
from matchcenter.proc import procVariable
import traceback
import json


g_iCheckTime = 0

def getPostFormat(dictData):
    dictParam = {'key':'123456', 'data':dictData}
    dictRetParam = {'json':json.dumps(dictParam)}
    return dictRetParam


@asyncio.coroutine
def updateMatchPlatform():
    global g_iCheckTime

    listMatchType = ["kog", "lol", "dota2"]
    gameTypeMapping = {2: "kog", 3: "lol", 4: "dota2"}

    objRedis = classDataBaseMgr.getInstance()

    # 获取上次的更新时间
    #iCheckTime = yield from objRedis.getLastAddCheckTime()
    iNowTime = timeHelp.getNow()
    if g_iCheckTime is None or g_iCheckTime == 0:
        #yield from objRedis.setLastAddCheckTime(iNowTime)
        g_iCheckTime = iNowTime
    else:

        dictGameKinds = {v: k for k, v in gameTypeMapping.items()}

        # 每5秒检查一次数据
        if (iNowTime - g_iCheckTime) >= 5:
            # 获取比赛竞猜的相关配置数据  竞猜玩法（第一滴血等）、竞猜目标（A队B队）

            try:
                for var_match_type in listMatchType:

                    try:
                        if procVariable.debug:

                            if not procVariable.dataDebug:
                                strPostUrl = matchcenter_config.dataPlatformReleaseBaseUrlForDebug + matchcenter_config.dataPlatformPostGetMatchData.format(
                                    var_match_type)
                            else:
                                strPostUrl = matchcenter_config.dataPlatformDebugBaseUrl + matchcenter_config.dataPlatformPostGetMatchData.format(var_match_type) + \
                                         matchcenter_config.debugAppend

                        else:
                            strPostUrl = matchcenter_config.dataPlatformReleaseBaseUrl + matchcenter_config.dataPlatformPostGetMatchData.format(
                                var_match_type)

                        strBeginTime = timeHelp.timestamp2Str(iNowTime)
                        strEndTime = timeHelp.timestamp2Str(iNowTime + 86400 * matchcenter_config.getMatchPreDay)  # 7天以后

                        dictParam = {'matchId': -1, 'startTime': strBeginTime, 'endTime': strEndTime}

                        dictPost = getPostFormat(dictParam)

                        dictHeader = {'Accept': 'text/html','Content-Type': 'application/x-www-form-urlencoded'}


                        with aiohttp.Timeout(100):
                            try:
                                client = aiohttp.ClientSession(response_class=aiohttpClientResponseWrap)
                                logging.debug("data center [{}]".format(strPostUrl))
                                # 请求数据中心的接口
                                result = yield from client.post(strPostUrl, data=dictPost,headers=dictHeader)

                                if result.status != 200:
                                    logging.error("get status[{}] game_type[{}]".format(result.status, var_match_type))
                                else:
                                    #print(dir(result))
                                    response = yield from result.read()     # 获取返回信息
                                    #logging.debug(response)
                                    dictResponse = json.loads(response)
                                    dictData = dictResponse['data']
                                    #print(dictData)
                                    if len(dictData) <= 0:
                                        continue

                                    for var_match_id,var_match_data in dictData.items():
                                        #查看本场比赛是否已经被添加进去
                                        matchId = var_match_type + var_match_id
                                        bIsAdd = yield from objRedis.checkPreMatchIdExist(matchId,var_match_type)
                                        if bIsAdd:
                                            #logging.info("{} matchId have already added".format(matchId))
                                            continue

                                        # 添加一个赛事
                                        objNewMatchData = matchData.classMatchData()
                                        objNewMatchData.strMatchId = matchId
                                        objNewMatchData.iMatchState = 0

                                        objNewMatchData.strMatchType = var_match_type
                                        objNewMatchData.strTeamAName = var_match_data['team1Name']
                                        objNewMatchData.strTeamBName = var_match_data['team2Name']

                                        objNewMatchData.iMatchState = 0  # 0:未开始  1：停止下注 2：比赛中  3：已结束 4：赛事被官方取消  5：后台主动关闭
                                        var_match_data['matchStartTime'] = var_match_data['matchStartTime']
                                        objNewMatchData.iMatchStartTimestamp = timeHelp.strToTimestamp(var_match_data['matchStartTime'])
                                        objNewMatchData.iMatchEndTimestamp = objNewMatchData.iMatchStartTimestamp + 3600

                                        objNewMatchData.iTeamAScore = 0
                                        objNewMatchData.iTeamBScore = 0

                                        objNewMatchData.strMatchName = var_match_data['eventName']
                                        objNewMatchData.iMatchRoundNum = int(var_match_data['roundCount'])

                                        objNewMatchData.arrayGuess = []  # Guess  GuessID = matchId + '_' + str(type)

                                        objNewMatchData.strTeamALogoUrl = var_match_data['team1Logo']
                                        objNewMatchData.strTeamBLogoUrl = var_match_data['team2Logo']

                                        #objNewMatchData.strTeamAId = var_match_data['team1Id']
                                        #objNewMatchData.strTeamBId = var_match_data['team2Id']


                                        yield from objRedis.addPreMatchForApproval(objNewMatchData)
                                        logging.info("save new have not template match[{}] matchAName[{}] matchBName[{}]".format(
                                            objNewMatchData.strMatchId,
                                            objNewMatchData.strTeamAName,
                                            objNewMatchData.strTeamBName))


                            finally:
                                yield from client.close()

                    except Exception as e:
                        logging.error(repr(e) + str(" game_type {}".format(var_match_type)))
                        logging.error(traceback.extract_stack())
                        continue
            finally:
                #yield from objRedis.setLastAddCheckTime(iNowTime)
                g_iCheckTime = iNowTime


def buildGuessData(guessId:str,objNewMatchData,var_round,var_playTypeObj,playName:str,playType,var_odds):
    objGuess = matchData.classGuessData()

    objGuess.strGuessId = guessId   # 竞猜id
    objGuess.strOwnerMatchId = objNewMatchData.strMatchId
    #objGuess.iGuessType = var_playTypeObj.strPlayType   # 玩法：第一滴血等等

    objGuess.strGuessName = playName    # 玩法名称
    #print(objGuess.strGuessName)

    objGuess.iGuessState = 0
    # 将当前竞猜数据放入当前比赛的arrayGuess中
    objNewMatchData.arrayGuess.append(objGuess.strGuessId)

    listRoundGuess = objNewMatchData.dictGuess.get(var_round, None)
    if listRoundGuess is None:
        objNewMatchData.dictGuess[var_round] = []
        objNewMatchData.dictGuess[var_round].append(objGuess.strGuessId)
    else:
        listRoundGuess.append(objGuess.strGuessId)

    # 先初始化
    for choose_item in var_playTypeObj.listChooseItem:
        objNew = matchData.CTR()    # 具体押注信息
        objNew.strId = choose_item['strDictKey']
        objNew.strChooseName = choose_item['strDictName']
        objNew.iTotalCoin = 0
        objGuess.dictCTR[objNew.strId] = objNew

    return objGuess