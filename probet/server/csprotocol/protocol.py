from csprotocol.protoBase import classProtoBase

getMatchList = "msgGetMatchList"    #获取比赛列表
guessBet = "msgGuessBet"            #玩家投注
getOneMatch = "msgGetOneMatch"      #获取单个比赛数据
getGuessBetList = "msgGetGuessBetList"   #正在竞猜投注的列表
getGuessResultList = "msgGetGuessResultList"   #已经结算竞猜投注的列表


heartBeat = "msgHeartBeat"          #心跳协议
connect = "msgConnect"              #登录协议
pushMatchList = "msgPushMatchList"  #推送比赛详细数据
pushMatchBasicList = "msgPushMatchBasicList"    #推送比赛简要数据，不包括竞猜项的推送
pushGuessList = "msgPushGuessList"  #推送单个竞猜项的数据
pushPlayerCoin = "msgPushPlayerCoin"#推送个人竞猜钱数据
pushPlayerCenterCoin = "msgPushPlayerCenterCoin"    #推送个人中心钱数据

pushGuessBetChangeResult = "msgPushGuessBetChangeResult"       #推送个人竞猜结果开奖变化
pushGuessBet = "msgPushGuessBet"                               #推送个人竞猜投注


pushPinboRepair = "msgPushPinboRepair"                         #推送平博維護變化
pushMessage = "msgPushPlayerMsg"                               #推送消息


class PC_msgHead(classProtoBase):
   def __init__(self):
       self.msgId = 0
       self.udid = ""
       self.token = ""
       self.accountId = ""
