from csprotocol.protoBase import classProtoBase,classProtoRet



class enumGetMatchType(object):
    getTypeAll = 0          #获取所有的
    getTypeToday = 1        #获取今日的
    getTypeLive = 2         #获取滚球的
    getTypeNotStart = 3     #获取未开始的


class protoChooseItem(classProtoBase):
    def __init__(self,ctrData):
        self.strId = ctrData.strId
        self.fRate = ctrData.fRate
        self.strChooseName = ctrData.strChooseName


class protoGuessItem(classProtoBase):
    def __init__(self,guessData):
        self.strGuessId = guessData.strGuessId
        self.arrayChooseItem = []
        for var_key,var_dict in guessData.dictCTR.items():
            self.arrayChooseItem.append(protoChooseItem(var_dict))

        self.strGuessName = guessData.strGuessName
        self.iGuessState = guessData.iGuessState  # 0:未开始 1:停止下注 2：竞猜中 3:正在结算 4：已结算 5：已经关闭 6：取消 7:无结果 8:已退款 9:已到账

        #self.strGuessResultDictKey = guessData.strGuessResultDictKey  # 结果 0：无结果  1：A 2：B ...等等
        self.strGuessResult = guessData.strGuessResult  # 比赛结束开的那个dictkey
        self.iHideFlag = guessData.iHideFlag# 0   1：隐藏
        self.iLimitPerAccount = guessData.iLimitPerAccount  # 单个用户押注限制值
        self.iRoundNum = guessData.iRoundNum
        self.strOwnerMatchId = guessData.strOwnerMatchId

class protoGuessItemList(classProtoBase):
    def __init__(self, iRound,listGuess):
        self.iRoundNum = iRound
        self.arrayGuess = []
        for var_guess in listGuess:
            self.arrayGuess.append(protoGuessItem(var_guess))

class protoMatchBasicItem(classProtoBase):
    def __init__(self, matchData):
        self.strMatchId = matchData.strMatchId
        self.strMatchType = matchData.strMatchType
        self.strTeamAName = matchData.strTeamAName
        self.strTeamBName = matchData.strTeamBName
        self.iMatchState = matchData.iMatchState  # 0:未开始  1：停止下注 2：比赛中  3：已结束 4：赛事被官方取消  5：后台主动关闭
        self.iMatchCreateTimestamp = matchData.iMatchCreateTimestamp
        self.iMatchStartTimestamp = matchData.iMatchStartTimestamp
        self.iMatchEndTimestamp = matchData.iMatchEndTimestamp

        self.iTeamAScore = matchData.iTeamAScore
        self.iTeamBScore = matchData.iTeamBScore
        self.strMatchName = matchData.strMatchName
        self.iMatchRoundNum = matchData.iMatchRoundNum
        self.iHideFlag = matchData.iHideFlag  # 隐藏flag
        self.strTeamALogo = matchData.strTeamALogoUrl
        self.strTeamBLogo = matchData.strTeamBLogoUrl



class protoMatchItem(protoMatchBasicItem):
    def __init__(self,matchData):
        super(protoMatchItem,self).__init__(matchData)
        self.arrayRound = []

    #构建某一场的竞猜
    def buildRoundGuessList(self,iRound,listGuess):

        temp = protoGuessItemList(iRound,listGuess)
        self.arrayRound.append(temp)

    # 构建某一场的竞猜
    def buildRoundGuess(self, iRound, objGuess):

        bFind = False
        for var_list in self.arrayRound:
            if iRound == var_list.iRoundNum:
                bFind = True
                var_list.arrayGuess.append(protoGuessItem(objGuess))
                break

        if not bFind:
            temp = protoGuessItemList(iRound,[objGuess])
            self.arrayRound.append(temp)


class protoGuessHistoryItem(classProtoBase):
    def __init__(self,guessHistory):
        self.iGuessBetUdid = guessHistory.strGuessUId
        self.strMatchId = guessHistory.strMatchId
        self.strGuessId = guessHistory.strGuessId
        self.strGuessName = guessHistory.strGuessName
        self.strTeamAName = guessHistory.strTeamAName
        self.strTeamBName = guessHistory.strTeamBName
        self.fRate = round(guessHistory.dictCTR[guessHistory.strChooseId].fRate,2)
        self.iBetCoin = "%.2f"%round(guessHistory.iBetCoin/100,2)
        self.strChooseName = guessHistory.dictCTR[guessHistory.strChooseId].strChooseName
        self.iWinCoin = "%.2f"%round(guessHistory.iBetCoin * (self.fRate - 1) / 100,2)


#- 获取比赛列表
class protoGetMatchListReq(classProtoBase):
    def __init__(self):
        self.iGetType = 0    #获取类型 enum  getMatchType


class protoGetMatchListResp(classProtoBase):
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.listMatchList = []  #protoMatchItem
        self.listStateCountList = []

# 获取单个比赛数据
class protoGetOneMatchReq(classProtoBase):
    def __init__(self):
        self.strMatchId = ""    #获取单个比赛的id


class protoGetOneMatchResp(classProtoBase):
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.listMatchList = []  # protoMatchItem

# 获取比赛的竞猜列表
class protoGetGuessBetListReq(classProtoBase):
    def __init__(self):
        pass


class protoGetGuessBetListResp(classProtoBase):
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.listGuessBetList = []  #protoGuessHistoryItem


# 获取比赛的结果列表
class protoGetGuessResultListReq(classProtoBase):
    def __init__(self):
        pass


class protoGetGuessResultListResp(classProtoBase):
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.listGuessResultList = []  #protoGuessHistoryItem




#***********************比赛推送***************************
class protoPushGuessData(classProtoBase,classProtoRet):
    def __init__(self):
        super(protoPushGuessData, self).__init__()
        self.listGuessList = [] #protoGuessItem


class protoPushMatchBasicData(classProtoBase,classProtoRet):
    def __init__(self):
        super(protoPushMatchBasicData, self).__init__()
        self.listMatchBasicList = [] #protoMatchBasicItem


class protoPushMatchData(classProtoBase,classProtoRet):
    def __init__(self):
        super(protoPushMatchData, self).__init__()
        self.listMatchList = [] #protoMatchItem

class protoPushBetResultData(classProtoBase,classProtoRet):
    def __init__(self):
        super(protoPushBetResultData, self).__init__()
        self.listGuessResultList = []   #protoGuessHistoryItem


class protoPushGuessBetData(classProtoBase,classProtoRet):
    def __init__(self):
        super(protoPushGuessBetData,self).__init__()
        self.listGuessBetList = []      #protoGuessHistoryItem


class protoPushCoinData(classProtoBase,classProtoRet):
    def __init__(self):
        super(protoPushCoinData, self).__init__()
        self.iCoin = 0                  #当前的金钱

#***********************竞猜相关的***************************
class protoGuessBetReq(classProtoBase):
    def __init__(self):
        self.iBetCoin = 0
        self.strMatchId = ""
        self.strChooseId = ""
        self.strGuessId = ""
        self.fBetRate = 0
        self.iBetRateIgnore = 0

class protoGuessBetResp(classProtoBase):
    def __init__(self):
        self.ret = 0
        self.retDes = ""



