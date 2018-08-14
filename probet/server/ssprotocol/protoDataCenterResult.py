
class result_msgId(object):
    msg_result = 1
    msg_back = 2
    msg_no_result = 3
    msg_award = 4
    msg_cancel_award = 5
    msg_cancel_result = 6
    msg_cancel_result_guessUId = 7      #取消某些押注单
    msg_result_guessUId = 8             #某些押注单单独开／使用guessdata 记录的result 来开奖
    msg_no_result_guessUId = 9  # 某些押注单单独开／使用guessdata 记录的result 来开奖

class ResultReq():
   def __init__(self):
       self.strMatchId = ""
       self.strGuessId = ""

       self.strDictKey = "" # A队  B队 or 第一项 第二项。。。多玩法
       self.iWinOrLose = 0  # 0 lose  1 win
       self.iHalfGet = 0    # 是不是 一半的收益 足球和篮球玩法开奖 字段
       self.strWinKey = ""

class BackReq():
    def __init__(self):
        self.strMatchId = ""
        self.strGuessId = ""

        self.strDictKey = "" #回退哪个 关键字的信息   #没有指定的话，就是全部退回

class AwardReq():
    def __init__(self):
        self.strMatchId = ""
        self.strGuessId = "" #暂时不传
        self.iAwardNum = 0
        self.iAwardType = 0
        self.iWinOrLose = 0 #奖励哪个 关键字的信息   #没有指定的话，就是全部奖励

class CancelAwardReq():
    def __init__(self):
        self.strMatchId = ""
        self.strGuessId = ""
        self.iWinOrLose = 0  # 取消奖励哪个 关键字的信息   #没有指定的话，就是取消全部奖励
        self.iCancelNum = 0

class CancelResultReq():
    def __init__(self):
        self.strMatchId = ""
        self.strGuessId = ""
        self.strDictKey = ""  # 取消奖励哪个 关键字的信息   #没有指定的话，就是取消全部奖励
        self.iBeginTime = 0
        self.iEndTime   = 0


class CancelResultByGuessUIdReq():
    def __init__(self):
        self.strMatchId = ""
        self.strGuessId = ""
