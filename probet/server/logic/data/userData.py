import random
import time
from logic.data.baseData import baseData
from config.activeConfig import activeConfig_cfg


class classBetCTR(baseData):
    def __init__(self):
        super(classBetCTR, self).__init__()
        self.strId = ""             # CTR 关键字 在字典中
        self.fRate = 0
        self.strChooseName = ""


class classUserBetHistory(baseData):
    def __init__(self):
        super(classUserBetHistory, self).__init__()
        self.strGuessUId = ""
        self.strMatchId = ""
        self.strMatchType = ""
        self.strGuessId = ""
        self.strGuessName = ""
        self.strChooseId = ""       # dictKey
        self.iRoundNum = 0          # roundindex
        self.iTime = 0
        self.iBetCoin = 0
        self.iWinCoin = 0
        self.iResult = 0            # 通guess state 的
        self.strResultId = ""       # 开奖的id
        self.iResultTime = 0        # 开奖的时间戳
        self.strAccountId = ""      # accountId
        self.dictCTR = {}           # classBetCTR
        self.strTeamAName = ""      # A队伍的名称
        self.strTeamBName = ""      # B队伍的名称


class classUserCoinHistory(baseData):
    def __init__(self):
        super(classUserCoinHistory, self).__init__()
        self.strOrderId = ""        # 流水单号
        self.iTime = 0              # 发生时间
        self.iCoin = 0              # 单位 rmb 分
        self.iBalance = 0           # 余额
        self.iTradeType = 0         # 详见coin的枚举类型  1：存款 2：取款 3：转账
        self.iTradeState = 0        # 1：成功 2：等待 3：取消 4：失败
        self.strAccountId = ""      # 单号归属账号id
        self.strIp = ""             # 客户的请求的ip
        self.iEndTime = 0           # 流水结束时间
        self.strTransFrom = ""      # 从哪转
        self.strTransTo = ""        # 转到哪个钱包,或者转到哪个银行卡（提款的时候用）
        self.strReviewer=""         # 审核人（线下充值的时候用）
        self.iValidWater=0          # 有效流水，返利时用
        self.strReason=""           # 原因  后台补发/扣款用
        self.strBankOrderId=""      #提款时记录银行流水号


class classMessageData(baseData):
    """消息"""
    def __init__(self):
        super(classMessageData, self).__init__()
        self.strMsgId = ""
        self.iMsgTime = 0         # 消息的创建时间
        self.iMsgType = 0         # 消息的类型 0:用户（系统） 1:公告 2:新闻 3:代理   详见消息枚举
        self.strMsgTitle = ""
        self.strMsgDetail = ""
        self.strAccountId = ""    # 收件人
        self.strSendFrom = ""     # 发送人id
        self.iReadFlag = 0        # 0：未读 1：已读
        self.isDelete=0           # 0.未删除 1.已删除
        self.iBroadcast = 0       # 0: 不轮播 1: 轮播


class classPayData(baseData):
    def __init__(self):
        super(classPayData, self).__init__()
        self.strPayOrder = ""
        self.strThirdPayOrder = ""
        self.strThirdPayName = ""
        self.strPayChannel = ""
        self.iOrderTime = 0
        self.strAccountId = ""
        self.iBuyCoin = 0
        self.strIp = ""
        self.iPayTime = 0
        self.strBank = ""
        self.iStatus = 1         # 1 未确认   2 已确认


class classActiveItem(baseData):
    def __init__(self):
        super(classActiveItem,self).__init__()
        self.iActiveId = 0      # 活动id 详见活动配置
        self.iActiveState = 0   # 0 未完成  1 已经完成 2 已经领奖
        self.iActiveTime = 0    # 激活的日期

        self.dictParam = {}     # 各种复合的数据

class classActiveTypeItem(baseData):
    def __init__(self):
        super(classActiveTypeItem, self).__init__()
        self.iActiveTypeId = 0
        self.dictParam = {}


class classActiveData(baseData):
    def __init__(self):
        super(classActiveData,self).__init__()
        self.strAccountId = ""
        self.dictActiveItem = {}
        self.dictActiveTypeItem = {}


    def getItemById(self,configId):
        # 通过id获取
        return self.dictActiveItem.get(configId,None)

    def getTypeItemByType(self,configType):
        return self.dictActiveTypeItem.get(configType,None)

    def getItemByTypeId(self,configType):

        for var_key,var_item in self.dictActiveItem.items():
            if int(activeConfig_cfg.get(str(var_item.iActiveId),{}).get("taskType",{})) == configType:
                return var_item
        return None

class classUserData(baseData):
    def __init__(self):
        super(classUserData,self).__init__()
        self.strAccountId = ""
        self.iUserType = 1           # 1:普通用户  2:代理用户
        self.strPhone = ""
        self.iCoin = 0               # 单位 rmb 元 放到redis hash 单独管理
        self.iGuessCoin = 0          # 电竞钱包
        self.iPingboCoin = 0         # 平博钱包
        self.iShabaCoin=0             #沙巴钱包
        self.iNotDrawingCoin = 0     # 不可提现额度
        self.iLastLoginTime = 0
        self.iRegTime = 0            # 注册时间
        self.strLastLoginUdid = ""
        self.strLastDeviceModal = ""
        self.strLastDeviceName = ""
        self.strToken = ""           # web端token
        self.strAppToken = ""        # 手机端token
        self.strWapToken = ""        # wap端token
        self.iLastBetTime = 0
        self.iPlatform = 0           # 0:无平台，自己平台  1:wx  2:qq
        self.strLastLoginIp = ""
        self.iLevel=0                # 用户等级
        self.iLevelValidWater = 0    # 当前等级下的流水值
        self.iStatus=0               # 0 正常，1冻结
        self.strLockReason=""        # 冻结原因
        self.iLockStartTime = 0
        self.iLockEndTime = 0        # 冻结时间
        self.iLogoutTime = 0
        self.strLoginAddress=""

        self.strHeadAddress = ""
        self.strPassword = ""
        self.strRealName = ""
        self.strSex = ""
        self.strBorn = ""
        self.strEmail = ""
        self.dictAddress = {}
        self.arrayBankCard = []
        self.iLastReceiveMsgTime = 0   # 最后一次获取消息的时间
        self.strTradePassword = ""     # 交易密码
        self.strAgentId = ""
        self.iFirstPayCoin = 0         # 第一次充值的额 单位 分
        self.iFirstPayTime = 0          # 第一次充值时间
        self.iLastPBCRefreshTime=0      #上一次平博钱包刷新时间

        # 活动相关
        # self.iLastPayTime = 0          # 上一次充值的时间
        # self.iMBWater = 0
        # self.iMBWaterTime = 0          # 上一次更新流水的时间


class classRepairData(baseData):
    def __init__(self):
        super(classRepairData, self).__init__()
        self.strRepairId = ""
        self.iTime = 0
        self.iStartTime = 0
        self.iEndTime = 0
        self.iRepairFlag = 0             # 0: 不开启 1:开启
        self.strAccountId = ""           # 管理员id
        self.iTimeOfUse = 0              # 耗时
        self.iPlatform = 0               # 1:平博体育    详见logic.enum.enumPlatform类型


class classAgentData(baseData):
    def __init__(self):
        super(classAgentData, self).__init__()
        self.strAgentId = ""
        self.strPhone = ""
        self.strEmail = ""
        self.strToken = ""               # web端token
        self.strAppToken = ""            # 手机端token
        self.strWapToken = ""            # wap端token
        self.iRegTime = 0                # 注册时间
        self.iCid = 0                    # 合营代码
        self.iStatus = 0                 # 0 正常，1冻结
        self.strLockReason = ""          # 冻结原因
        self.iLockStartTime = 0
        self.iLockEndTime = 0            # 冻结时间


# 佣金报表
class classAgentCommissionData(baseData):
    def __init__(self):
        super(classAgentCommissionData, self).__init__()
        self.strBillId = ""              # 单号
        self.strAgentId = ""             # 代理id
        self.iTime = 0                   # 生成时间
        self.iYear = 0                   # 日期
        self.iMonth = 0                  # 日期
        self.iNewAccount = 0             # 新增用户
        self.iActiveAccount = 0          # 活跃用户
        self.iProbetWinLoss = 0          # 电竞输赢
        self.iPingboWinLoss = 0          # 平博输赢
        self.iWinLoss = 0                # 总输赢
        self.fProbetRate = 0             # 电竞平台费率
        self.fPingboRate = 0             # 平博平台率
        self.iProbetCost = 0             # 电竞平台费
        self.iPingboCost = 0             # 平博平台费
        self.iPlatformCost = 0           # 平台费
        self.iDepositDrawingCost = 0.0   # 充提手续费
        self.iBackWater = 0              # 反水
        self.iBonus = 0                  # 活动奖金
        self.iWater = 0                  # 流水
        self.iNetProfit = 0              # 净利润
        self.iBalance = 0                # 月结余
        self.fCommissionRate = 0.00      # 佣金比
        self.iCommission = 0             # 佣金
        self.iStatus = 1                 # 佣金状态   0：已发放  1：未发放 2：未达条件  3：未到结算时间
        self.iHandleTime = 0             # 发放时间
        self.strReviewer = ""            # 审核人（佣金发放的时候用）


# 代理申请信息
class classApplyForAgent(baseData):
    def __init__(self):
        super(classApplyForAgent, self).__init__()
        self.iTime = 0                   # 申请时间
        self.strAgentId = ""             # 代理账号
        self.strQQ = ""                  # QQ号
        self.strWebsite = ""             # 网址
        self.strDesc = ""                # 推广介绍
        self.iStatus = 0                 # 申请状态  0:已通过 1:待审核 2:已拒绝 3:已终止


# 代理配置
class classConfig(baseData):
    def __init__(self):
        super(classConfig, self).__init__()
        self.strName = ""
        self.iRate = 0           # 费率=iRate/1000
        self.iKind = 1           # 1:平台费率 2:手续费率 3:佣金比例


