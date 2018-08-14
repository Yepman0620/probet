from logic.data.baseData import baseData


class CTR(baseData):
    def __init__(self):
        super(CTR, self).__init__()
        self.strId = "" #CTR 关键字 在字典中
        self.fRate = 0
        self.strChooseName = ""
        self.iTotalCoin = 0         #押注金额
        self.iTotalBetNum = 0       #押注次数
        self.iReturnCoin = 0        #赔付金额



class classGuessData(baseData):
    def __init__(self):
        super(classGuessData, self).__init__()
        self.strGuessId = ""
        self.dictCTR = {}
        #self.iGuessType = 0         # 字符串，bo1_blood TODO modify str prefix
        self.strGuessName = ""
        self.iGuessState = 0        # 0:未开始 1:停止下注 2：竞猜中 3:正在结算 4：已结算 5：已经关闭 6：取消 7:无结果 8:已退款 9:已到账

        #self.strGuessResultDictKey = 0       #结果 0：无结果  1：A 2：B ...等等
        self.strGuessResult = ""    #比赛结束开的那个dictkey
        self.iHideFlag = 0          # 0   1：隐藏
        self.iLimitPerAccount = 1000000   #单个用户押注限制值

        self.strOwnerMatchId = ""
        self.iRoundNum = 0

        self.iCancelResultFlag = 0  #是否取消过结果
        self.iCancelResultBeginTime = 0
        self.iCancelResultEndTime = 0

        self.iFixReturnRate = 0  # 锁定返还率 0 不锁定  1锁定


class classMatchData(baseData):
    def __init__(self):
        super(classMatchData, self).__init__()
        self.strMatchId = ""
        self.strMatchType = ""
        self.strTeamAName = ""
        self.strTeamBName = ""
        self.iMatchState = 0        # 0:未开始  1：停止下注 2：比赛中  3：已结束 4：赛事被官方取消  5：后台主动关闭
        self.iMatchCreateTimestamp = 0
        self.iMatchStartTimestamp = 0
        self.iMatchEndTimestamp = 0

        self.iTeamAScore = 0
        self.iTeamBScore = 0

        self.strMatchName = ""
        self.iMatchRoundNum = 0

        self.arrayGuess = []        #Guess  GuessID = matchId + '_' + str(type)
        self.dictGuess = {}         #和上面的array对应的，这个里面的key value key是场次 0 代表 全局场次的玩法 1代表bo1的玩法,value 是数组
        self.arrayAwardGuess = []

        self.strTeamALogoUrl = ""
        self.strTeamBLogoUrl = ""

        self.iHideFlag = 0          #隐藏flag
        self.iAwardFlag = 0
        self.iAwardNum = 0          #奖励数量
        self.iAwardType = 0         #0 金币 1 钻石
        self.iWinOrLose = 0         #0 输的 1赢的 2 全部都奖励
        self.iCancelResultFlag = 0        #0 未取消 1 取消
        self.arrayCancelResultGuessId = []  #取消结果的 竞猜id

