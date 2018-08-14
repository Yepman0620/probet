"""
redis 操作数据key 的定义文件
"""
#####用户相关
playerDataHash = "playerDataHash"
playerLockIdKey = "playerLockIdKey_{}"
playerLockTimeKey = "playerLockTimeKey_{}"
playerDataKeyDirtyList = "playerDataKeyDirtyList"
playerDataKeyNewList = "playerDataKeyNewList"
playerCoinHash = "playerCoinHash"


#####代理相关的
agentDataHash = "agentDataHash"
agentDataKeyNewList = "agentDataKeyNewList"
agentDataKeyDirtyList = "agentDataKeyDirtyList"


###比赛相关的
matchDataHash = "matchDataHash"
matchLockIdKey = "matchLockIdKey_{}"
matchLockTimeKey = "matchLockTimeKey_{}"
matchDataKeyDirtyList = "matchDataKeyDirtyList"
matchDataKeyNewList = "matchDataKeyNewList"

###竞猜项有关的
guessDataHash = "guessDataHash"
guessLockIdKey = "guessLockIdKey_{}"
guessLockTimeKey = "guessLockTimeKey_{}"
guessDataKeyDirtyList = "guessDataKeyDirtyList"
guessDataKeyNewList = "guessDataKeyNewList"


###充值相关的
payDataHash = "payDataHash"
payLockIdKey = "payLockIdKey_{}"
payLockTimeKey = "payLockTimeKey_{}"
payDataKeyDirtyList = "payDataKeyDirtyList"
payDataKeyNewList = "payDataKeyNewList"


###活动相关的
activeDataHash = "activeDataHash"
activeLockIdKey = "activeLockIdKey_{}"
activeLockTimeKey = "activeLockTimeKey_{}"
activeDataKeyDirtyList = "activeDataKeyDirtyList"
activeDataKeyNewList = "activeDataKeyNewList"


### 消息相关
sysMsgNewKeyList="sysMsgKeyNewList"
sysMsgKeyDirtyList="sysMsgKeyDirtyList"
noticeMsgNewKeyList="noticeMsgNewKeyList"
noticeMsgKeyDirtyList="noticeMsgKeyDirtyList"
newsMsgNewKeyList="newsMsgNewKeyList"
newsMsgKeyDirtyList="newsMsgKeyDirtyList"
activeMsgNewKeyList="activeMsgNewKeyList"
activeMsgKeyDirtyList="activeMsgKeyDirtyList"
agentMsgNewKeyList = "agentMsgNewKeyList"
agentMsgKeyDirtyList="agentMsgKeyDirtyList"

### 维护相关
repairDataNewKeyList="repairDataNewKeyList"
repairDataKeyDirtyList="repairDataKeyDirtyList"


### 计算流水相关
pinboLoginIdWaterDirtyList = "pinboLoginIdWaterDirtyList"
probetAccountWaterDirtyList ="probetAccountWaterDirtyList"

### 短链接相关的
urlShortStr = "urlShortStr"


###计算时间相关的
#计算日流水相关的
calcDayWaterTimeStr = "calcDayWaterTimeStr"
#计算月流水相关的
calcMonthWaterTimeStr = "calcMonthWaterTimeStr"
#计算排行榜相关的
calcRankTimeStr = "calcRankTimeStr"
#计算月佣金相关的
calcMonthCommissionTimeStr = "calcMonthCommissionTimeStr"
#计算月初到现在累计佣金相关的
calcMonthByDayCommissionTimeStr = "calcMonthByDayCommissionTimeStr"

