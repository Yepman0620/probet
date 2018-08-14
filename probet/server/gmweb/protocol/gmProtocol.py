
gameType=["kog","lol","dota2","csgo"]

gameTypeMap = {"lol":"英雄联盟","kog":"王者荣耀","dota2":"刀塔2","csgo":"反恐精英"}#,"football":"足球","basketball":"篮球"，"dota2":"刀塔2"}
pingboBetType={1:"1x2 标准盘 ",2:"Handicap 让球盘",3:"Over Under 总进球",4:"主队_总得分",5:"客队_总得分",6:"混合过关",8:"MANUAL_PLAY",97:"Odd Even 单双 ",99:"优生冠军"}
pingboOddsFormat={0:"AM 美式盘",1:"欧洲盘",2:"HK 香港盘",3:"ID 印尼盘",4:"MY 马来盘",}
playType={1:"一血",2:"二串一",3:"独赢"}

def getGraphIndex(fRate:float):
    temp = round(fRate,1)
    if 1.0 <= temp and temp < 2.0:
        return temp
    elif temp >= 2.0 and temp < 3.0:
        check = temp * 10
        left = check % 2
        return temp - left/10

    elif temp >= 3.0 and temp < 5:
        check = temp * 10
        left = check % 5
        return temp - left/10

graphRange = [1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.2,2.4,2.6,2.8,3.0,3.5,4.0,4.5,5.0]


#每个赛事的数据,一下是协议的分割线

class classGmPlayData():
    def __init__(self):

        self.strPlayTypeName = ""
        self.dictTeamInfo = {} #参考CTR()
        self.iGuessState = 0
        self.strGuessId = ""
        self.iRoundNum = 0
        self.iHideFlag = 0
        self.strGuessResult = ""


class classGmMatchTotal():
    def __init__(self):
        self.arrMatchData = []
        self.iTotalNum = 0

class classGmMatchData():
    def __init__(self):

        self.strMatchId = ""
        self.strProjectName = ""
        self.strActivityName = ""
        self.strTeam1Name = ""
        self.strTeam1Logo = ""
        self.strTeam2Name = ""
        self.strTeam2Logo = ""
        self.iGameState = 0
        self.strGameStartTime = 0
        self.arrPlayTypeList = []   # 玩法列表
        self.iSupportA = 0
        self.iSupportB = 0
        self.iHideFlag = 0
        #self.strTeamAId = ""
        #self.strTeamBId = ""
        self.iTeamAScore = 0
        self.iTeamBScore = 0

        self.iAwardFlag = 0
        self.iAwardNum = 0
        self.iAwardType = 0
        self.iWinOrLose = 0
        self.iCancelResultFlag = 0
        self.iCancelResultBeginTime = 0
        self.iCancelResultEndTime = 0


class classGmMatchLiveData():
    def __init__(self):

        self.strMatchId = ""
        self.strProjectName = ""
        self.strActivityName = ""
        self.strTeam1Name = ""
        self.strTeam1Logo = ""
        self.strTeam2Name = ""
        self.strTeam2Logo = ""
        self.iGameState = 0
        self.strGameStartTime = 0
        #self.strMainLiveUrl = ""
        #self.strSlaveLiveUrl = ""


class classGmChooseBasicData():
    def __init__(self):
        self.fRate = 0          #赔率
        self.fReturnBet = 0     #赔付
        self.fTotalBetCoin = 0      #总共押注
        self.iTotalBetNum = 0       #押注次数
        self.strChooseId = ""
        self.strChooseName = ""

class classGmMatchBasicItem():
    def __init__(self):
        self.strGuessId = ""
        self.strGuessName = ""
        self.arrChooseBasicData = []
        self.strResult = ""

class classGmMatchBasicData():
    def __init__(self):
        self.strMatchId = ""
        self.arrGuessBasicItem = []



class classGmMatchDetailData():
    def __init__(self):
        self.strMatchId = ""
        self.iTotalJoin = 0
        self.iRefundLock = 0 #是否锁定返还率
        self.fRefund = 0
        self.iLimitCoin = 0 #押注上限
        self.fEquivalenceRatio = 0
        self.dictGraphItem={} #chooseId : [x,x,x,x,x,x,x...]
        self.dictGraphItemLastMinute = {}  # chooseId : [x,x,x,x,x,x,x...]


class classGmRecentBetItem():
    def __init__(self):
        self.strAccountId = ""
        self.strChooseId = ""
        self.iBetNum = 0

class classGmRecentPlayerData():
    def __init__(self):
        self.arrCurrentBetInfo = []
        self.iCursor = 0
        self.arrChooseName = []


class classGmAllPlayerData():
    def __init__(self):
        self.arrCurrentBetInfo = []
        self.arrChooseName = []
        self.iTotal = 0


class classGmMergeMatchDetailDataAndRecentPlayerData():
    def __init__(self):
        self.data1 = None #MatchDetailData
        self.data2 = None #RecentPlayerData
