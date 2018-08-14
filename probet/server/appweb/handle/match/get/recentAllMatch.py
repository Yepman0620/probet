import asyncio
from lib.jsonhelp import classJsonDump
from logic.data.matchData import classMatchData
from datawrapper.dataBaseMgr import classDataBaseMgr


class cMatch():
    def __init__(self):
        self.strMatchId = ""
        self.strMatchType = ""
        self.strTeamAName = ""
        self.strTeamBName = ""
        self.iMatchState = 0
        self.iMatchStartTimestamp = 0
        self.strMatchName = ""
        self.iMatchRoundNum = 0

    def buildByClassMatchData(self,matchData:classMatchData):
        for var_key in self.__dict__.keys():
            if var_key in matchData.__dict__:
                self.__dict__[var_key] = matchData.__dict__[var_key]

class cMatchList():
    def __init__(self):
        self.strType = ""
        self.arrayMatch = []

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@asyncio.coroutine
def handleHttp(dictParam: dict):
    objResp = cResp()
    objDataIns = classDataBaseMgr.getInstance()

    listLoLMatchDatas = yield from objDataIns.getMatchDataListByRange(0, 6, "lol")
    listDota2MatchDatas = yield from objDataIns.getMatchDataListByRange(0, 6, "dota2")
    listKogMatchDatas = yield from objDataIns.getMatchDataListByRange(0, 6, "kog")
    listCsgoMatchDatas = yield from objDataIns.getMatchDataListByRange(0, 6, "csgo")


    objList = cMatchList()
    objList.strType = "lol"

    for var in listLoLMatchDatas:
        objNewMatch = cMatch()
        objNewMatch.buildByClassMatchData(var)
        objList.arrayMatch.append(objNewMatch)
    objList.arrayMatch.reverse()
    objResp.data.append(objList)

    objList = cMatchList()
    objList.strType = "dota2"

    for var in listDota2MatchDatas:
        objNewMatch = cMatch()
        objNewMatch.buildByClassMatchData(var)
        objList.arrayMatch.append(objNewMatch)
    objList.arrayMatch.reverse()
    objResp.data.append(objList)

    objList = cMatchList()
    objList.strType = "kog"
    for var in listKogMatchDatas:
        objNewMatch = cMatch()
        objNewMatch.buildByClassMatchData(var)
        objList.arrayMatch.append(objNewMatch)
    objList.arrayMatch.reverse()
    objResp.data.append(objList)

    objList = cMatchList()
    objList.strType = "csgo"
    for var in listCsgoMatchDatas:
        objNewMatch = cMatch()
        objNewMatch.buildByClassMatchData(var)
        objList.arrayMatch.append(objNewMatch)
    objList.arrayMatch.reverse()
    objResp.data.append(objList)

    return classJsonDump.dumps(objResp)

