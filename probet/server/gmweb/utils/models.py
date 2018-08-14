import logging
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, MetaData, Table, ForeignKey, BigInteger, Text, SmallInteger, Float, \
    PickleType, DECIMAL,JSON
from werkzeug.security import generate_password_hash,check_password_hash


Base=declarative_base()

def password_hash(password):
    passwordHash = generate_password_hash(password)
    return passwordHash

def check_password(passwordHash,password):
    return check_password_hash(passwordHash, password)

class BaseModel(object):
    #模型基类
    from lib.timehelp.timeHelp import getNow
    create_time=Column(Integer,default=getNow())
    update_time=Column(Integer,default=getNow())


class Administer(Base,BaseModel):
    # 用户类
    __tablename__='dj_admin_account'
    id=Column(Integer,primary_key=True,autoincrement=True)
    accountId = Column(String(32),nullable=False,unique=True)
    passwordHash = Column(String(128),nullable=False)
    # 获取角色
    role_id=Column(Integer,ForeignKey('dj_admin_role.id'),default='',nullable=True)
    token=Column(String(128*2),nullable=True)
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

    @property
    def password_hash(self):
        from error.errorCode import errorLogic, exceptionLogic
        logging.debug(errorLogic.attributte_cannot_visit)
        raise exceptionLogic(errorLogic.attributte_cannot_visit)

    @password_hash.setter
    def password_hash(self,password):
        self.passwordHash=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.passwordHash,password)


#角色-权限表
role_action=Table(
    'dj_admin_role_action',Base.metadata,
    Column('role_id',Integer,ForeignKey('dj_admin_role.id'),primary_key=True),
    Column('action_id',Integer,ForeignKey('dj_admin_action.id'),primary_key=True)
)

class Role(Base,BaseModel):
    #角色
    __tablename__='dj_admin_role'
    id=Column(Integer,primary_key=True,autoincrement=True)
    role_name=Column(String(32),nullable=False,unique=True)
    # 获取该角色下所有用户
    accounts=relationship('Administer',backref='role',lazy='dynamic')
    actions = relationship("Action", secondary=role_action)  # 根据角色获取所有权限
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

    def get_actions_name(self):
        # 权限名
        actions = []
        for action in self.actions:
            actions.append(action.action_name)

        return actions

    def get_actions_id_name(self):
        actions=[]
        for action in self.actions:
            actions.append([action.id,action.action_name])

        return actions


class Action(Base,BaseModel):
    # 权限
    __tablename__='dj_admin_action'
    id=Column(Integer,primary_key=True,autoincrement=True)
    action_name=Column(String(32),nullable=False,unique=True)
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

class UserInfo(Base):
    #用户信息
    __tablename__='dj_account'
    accountId=Column(String(64), primary_key=True)
    #nick=Column(String(255),default="", nullable=True)
    userType=Column(SmallInteger(),default=0,nullable=False)  # 1:普通用户 2:代理用户
    phone=Column(String(255), default="", nullable=True)
    coin=Column(BigInteger(), default=0)
    guessCoin=Column(BigInteger(), default=0)
    pingboCoin=Column(BigInteger(), default=0)
    shabaCoin=Column(BigInteger(),default=0)
    notDrawingCoin=Column(BigInteger(), default=0)
    passwordMd5=Column(String(255), default="", nullable=False)
    # secret=Column(String(255), default="", nullable=False)
    regTime=Column(Integer(), default=0, nullable=False)
    email=Column(String(255), default="", nullable=True)
    loginTime=Column(Integer(), default=0, nullable=True)
    loginIp=Column(String(255), default="", nullable=True)
    loginAddress=Column(String(255),default="",nullable=True) #登录地址
    loginDeviceUdid=Column(String(255), default="", nullable=True)
    loginDeviceModel=Column(String(255), default="", nullable=True) #登录设备模型
    loginDeviceName=Column(String(255), default="", nullable=True)  #登录设备名称
    logoutTime=Column(Integer(),default=0,nullable=True)
    lastBetTime=Column(Integer(), default=0, nullable=True)
    platform=Column(Integer(), default=0, nullable=True)
    # invalid=Column(Integer(), default=0,nullable=False)
    # lastReceviveMsgTime=Column(Integer(), default=0, nullable=False)
    firstPayCoin=Column(Integer(),default=0,nullable=True)
    firstPayTime=Column(Integer(),default=0,nullable=True)
    headAddress=Column(String(255), default="", nullable=True)
    realName=Column(String(255), default="", nullable=True)
    sex=Column(String(32), default="", nullable=True)
    born=Column(String(255), default="", nullable=True)
    address=Column(String(512), default="", nullable=True)
    bankcard=Column(String(1024), default="", nullable=True)
    tradePasswordMd5=Column(String(255), default="", nullable=True)
    status=Column(SmallInteger(),default=0,nullable=True) #0 正常，1冻结
    lockStartTime=Column(Integer(),default=0,nullable=True) #封停开始时间
    lockEndTime=Column(Integer(),default=0,nullable=True) #封停结束
    lockReason=Column(String(512),default="",nullable=True) #封停原因
    level=Column(Integer(),default=0,nullable=False) #等级
    levelValidWater = Column(Integer(), default=0, nullable=True)  # 等级下的有效流水值
    agentId = Column(String(64), default="",nullable=False,index=True)  # 代理id
    lastPBCRefreshTime = Column(Integer(),default=0,nullable=True) #上一次平博钱包刷新时间
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

class BetInfo(Base):
    #比分信息..投注记录表
    __tablename__='dj_bet'
    guessUId=Column( String(64), primary_key=True) #竞猜id
    matchId=Column(String(255), default="", nullable=False, index=True)
    matchType=Column(String(255), default="", nullable=False) #比赛类型
    guessId=Column(String(255), default="", nullable=False, index=True)# 竞猜项id
    chooseId=Column(String(255), default="", nullable=False)  #投注项id
    guessName=Column(String(128),default='',nullable=False)     #比赛名称
    roundNum=Column(Integer(), default=0, nullable=False)  # 投注轮
    time=Column(Integer(), default="", nullable=False, index=True) # 创建时间
    betCoin=Column(Integer(), default=0, nullable=False)  #下注金额 ：分
    winCoin=Column(Integer(), default=0, nullable=False)  #赢的钱：分
    result=Column(Integer(), default=0, nullable=False, index=True) # 竞猜状态
    resultId=Column(String(255), default="", nullable=False, index=True)  #开奖项
    resultTime=Column(Integer(), default=0, nullable=False, index=True)  #开奖时间
    accountId=Column(String(255), default="", nullable=False, index=True)
    ctr=Column(String(512), default="", nullable=False)   #
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

class GuessInfo(Base):
    #竞猜信息
    __tablename__ = 'dj_match_guess'
    guessId=Column(String(255), primary_key=True)
    guessName=Column(String(255), default="", nullable=False) #竞猜名
    guessState=Column(Integer(), default=0, nullable=False) #竞猜状态
    # matchId=Column(String(255), default="")
    hideFlag=Column(Integer(), default=0, nullable=False) # 是否隐藏
    limitPerAccount=Column(Integer(), default=0, nullable=False) #单注上限
    ownerMatchId=Column(String(255), default="", nullable=False) # 属于哪个比赛
    roundNum=Column(Integer(), default=0, nullable=False) #回合
    cancelResultFlag=Column(String(255), default="", nullable=False) # 竞猜项是否取消
    cancelResultBeginTime=Column(Integer(), default=0, nullable=False) #取消时间
    cancelResultEndTime=Column(Integer(), default=0, nullable=False)
    # ctr
    ctr=Column(String(512), default="")
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

class MatchInfo(Base):
    # 比赛信息
    __tablename__='dj_match'
    matchId=Column(String(255), default="", primary_key=True)
    matchTeamALogo=Column(String(255), default="", nullable=False) #比赛
    teamAName=Column(String(255), default="", nullable=False)
    matchTeamBLogo=Column(String(255), default="", nullable=False)
    teamBName=Column(String(255), default="", nullable=False)
    matchName=Column(String(255), default="", nullable=False)
    # matchBO=Column(Integer(), default="")
    matchState=Column(Integer(), default=0, nullable=False, index=True)
    teamAScore=Column(Integer(), default=0, nullable=False)
    teamBScore=Column(Integer(), default=0, nullable=False)
    matchStartTime=Column(Integer(), default=0, nullable=False, index=True)
    matchEndTime=Column(Integer(), default=0, nullable=False)
    matchRoundNum=Column(Integer(), default=0, nullable=False)
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

class PayInfo(Base):
    # 支付信息
    __tablename__='dj_pay_order'
    payOrder=Column(String(64), primary_key=True)
    thirdPayOrder=Column(String(255), default="", nullable=True, index=True) #线下支付没有
    thirdPayName=Column(String(64), default="", nullable=True, index=True) #线下支付渠道名称
    payChannel=Column( String(255), default="", nullable=False,index=True) #支付方式 unionpay  qq  alipay  offline
    accountId=Column(String(255), default="", nullable=False, index=True)
    orderTime=Column(Integer(), default=0, nullable=False, index=True)
    buyCoin=Column(Integer(), default="", nullable=False)
    payTime=Column(Integer(), default=0, nullable=False, index=True)
    ip=Column(String(255), default="", nullable=False, index=True)
    bank=Column(String(255), default="", nullable=False, index=True) #银行卡
    status=Column(SmallInteger(), default=1, nullable=False)  # 1.未确认, 2.已确认
    __table_args__ = {
            'mysql_charset': 'utf8mb4'
        }

class HistoryCoinInfo(Base):
    # 历史金币，流水
    __tablename__='dj_coin_history'
    orderId=Column(String(64), primary_key=True)
    orderTime=Column(Integer(), default=0, nullable=False, index=True)
    coinNum=Column(Integer(), default=0, nullable=False, index=True)
    balance = Column(Integer(), default=0, nullable=True)  # 余额
    tradeType=Column(Integer(), default=0, nullable=False, index=True) # 详见coin的枚举类型  1：存款 2：取款 3：转账
    tradeState=Column(Integer(), default=0, nullable=False, index=True) # 1：成功 2：等待 3：取消 4：失败
    accountId=Column(String(255), default="", nullable=False, index=True)
    ip=Column(String(32), default="", nullable=False)
    endTime=Column(Integer(), default=0, nullable=False, index=True)
    transFrom = Column(String(255), default="", nullable=False)  # 从哪转
    transTo=Column(String(255), default="", nullable=False)   #转到哪
    reviewer=Column(String(32),default="",nullable=True) # 审核人
    validWater=Column(Integer(),default=0,nullable=True)  #有效流水，返利时用
    reason=Column(String(64),default="",nullable=True)  #原因，后台补发、扣款用
    bankOrderId=Column(String(128),default="",nullable=True)  #提款时记录银行流水号
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

class UserMsg(Base):
    # 用户邮件信息
    __tablename__='dj_all_msg'
    id=Column(Integer(),primary_key=True)
    msgId=Column(String(64),nullable=False)
    msgTime=Column(Integer(), default=0, nullable=False)
    msgTitle=Column(String(255), default="", nullable=False)
    msgDetail=Column(Text(length=65536), default="", nullable=False)
    readFlag=Column(SmallInteger(), default=0, nullable=False)
    sendTo=Column(String(32),default=0,nullable=False)
    sendFrom=Column(String(32),default="",nullable=False)
    type=Column(SmallInteger(), default=0, nullable=False)  # 0.用户消息，1.公告消息，2.新闻消息，3.代理消息
    broadcast=Column(SmallInteger(), default=0, nullable=False)  # 0.不轮播, 1.轮播
    isdelete=Column(SmallInteger(), default=0, nullable=True)
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

class ShaBaWagers(Base):
    oddsType_choices = {1:'MalayOdds',2:'HongKongOdds',3:'DecimalOdds',4:'IndoOdds',5:'AmericanOdds'}
    currencyType_choices={}
    __tablename__='dj_shaba_wagers'
    transId=Column(BigInteger(),primary_key=True)
    vendorMember_id=Column(String(50),default='',nullable=False)#用户名
    oddsType=Column(SmallInteger(),default=0,nullable=False)#赔率类型
    odds=Column(Float(),default=0,nullable=False) #赔率
    stake=Column(Float(),default=0,nullable=False)#投注额
    transActionTime=Column(Integer(),default=0,nullable=False) #投注时间
    currency=Column(Integer(),default=0,nullable=False) #币种id
    winLostDateTime=Column(Integer(),default=0,nullable=False)#结算时间
    ticketStatus=Column(String(10),default='',nullable=False) #状态
    winLostAmount=Column(Float(),default=0,nullable=False) #实际输赢
    messageData=Column(JSON(),default='',nullable=True) #整体JSON数据
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

class PinBoWagers(Base):
    # 平博竞猜账单
    __tablename__='dj_pinbo_wagers'
    wagerId=Column(Integer(), primary_key=True)
    oddsFormat=Column(Integer(), default=0, nullable=False) #赔率类型
    odds=Column(Float(), default=0, nullable=False, index=True) #赔率
    stake=Column(Float(), default=0, nullable=False) # 赌注
    toWin=Column(Float(), default=0, nullable=False) #预期收益
    toRisk=Column(Float(), default=0, nullable=False) #风险多少
    winLoss=Column(Float(), default=0, nullable=False, index=True) #实际输赢
    currencyCode=Column(String(32), default="", nullable=False) #币种
    loginId=Column(String(64), default="", nullable=False, index=True)
    wagerDateFm=Column(Integer(), default=0, nullable=False,index=True) # 下注时间
    settleDateFm = Column(Integer(), default=0, nullable=False,index=True)  # 开奖时间
    status=Column(String(32),default='',nullable=True) #状态
    messageData=Column(JSON(), default="", nullable=True)
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

class Banner(Base,BaseModel):
    # 轮播图
    __tablename__='dj_banner'
    id=Column(Integer(),primary_key=True,autoincrement=True)
    image_url=Column(String(1024),default='',nullable=False)
    index=Column(SmallInteger(),default=0)
    link_url=Column(String(1024),default='',nullable=False)
    title=Column(String(128),default='',nullable=False)
    addAccount=Column(String(32),default='',nullable=False)
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

class OfflineAccountRecharge(Base,BaseModel):
    # 线下充值账号
    __tablename__ = 'dj_offline_account_recharge'
    id = Column(Integer(), primary_key=True,autoincrement=True)
    name=Column(String(64),default='',nullable=False)
    accountId=Column(String(64),default='',nullable=False)
    bank=Column(String(64),default='',nullable=True) # 银行卡账号有
    bankInfo=Column(String(255), default="", nullable=True)
    status=Column(SmallInteger(),default=0,nullable=False)  # 0 上线，1 暂停使用
    kind=Column(SmallInteger(),default=0,nullable=False)  # 0支付宝 1银行卡 2微信
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

class RepairData(Base):
    # 平台维护记录
    from lib.timehelp.timeHelp import getNow
    __tablename__ = 'dj_repair'
    repairId = Column(String(128), primary_key=True)
    create_time = Column(Integer(), default=getNow())
    start_time = Column(Integer(), default=0, nullable=False)
    end_time = Column(Integer(), default=0, nullable=False)
    repairFlag = Column(SmallInteger(), default=0, nullable=False)
    accountId = Column(String(64), default='', nullable=False)
    platform = Column(SmallInteger(), default=0, nullable=False)
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

class AgentInfo(Base):
    # 代理表
    __tablename__ = 'dj_agent'
    agentId = Column(String(64), primary_key=True)
    regTime = Column(Integer(), default=0, nullable=False)
    code = Column(Integer(), nullable=False)
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

class AgentConfigInfo(Base):
    # 代理配置信息
    __tablename__ = 'dj_agent_config'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    pingboRate = Column(Float(), default=0, nullable=False)          # 平博平台费率
    probetRate = Column(Float(), default=0, nullable=False)          # 电竞竞猜费率
    qqRate = Column(Float(), default=0, nullable=False)              # QQ扫码手续费率
    alipayRate = Column(Float(), default=0, nullable=False)          # 支付宝扫码手续费率
    unionpayRate = Column(Float(), default=0, nullable=False)        # 银联扫码手续费率
    bankTransferRate = Column(Float(), default=0, nullable=False)    # 银行卡转账手续费率
    alipayTransferRate = Column(Float(), default=0, nullable=False)  # 银行卡转账手续费率
    weixinTransferRate = Column(Float(), default=0, nullable=False)  # 微信转账手续费率
    drawingRate = Column(Float(), default=0, nullable=False)         # 提款手续费率
    Lv1 = Column(Float(), default=0, nullable=False)  # 佣金比例档次
    Lv2 = Column(Float(), default=0, nullable=False)
    Lv3 = Column(Float(), default=0, nullable=False)
    Lv4 = Column(Float(), default=0, nullable=False)
    Lv5 = Column(Float(), default=0, nullable=False)
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

class AgentCommission(Base):
    # 代理佣金报表
    __tablename__ = 'dj_agent_commission'
    billId = Column(String(64), primary_key=True)                       # 账单号
    billTime = Column(Integer(), default=0, nullable=False)             # 生成时间
    agentId = Column(String(255), default="", nullable=False)           # 代理Id
    dateYear = Column(Integer(), default="", nullable=False)            # 年
    dateMonth = Column(Integer(), default="", nullable=False)           # 月
    newAccount = Column(Integer(), default=0, nullable=True)            # 新增用户
    activeAccount = Column(Integer(), default=0, nullable=False)        # 活跃用户
    probetWinLoss = Column(Integer(), default=0, nullable=False)        # 电竞总输赢
    pingboWinLoss = Column(Integer(), default=0, nullable=False)        # 平博总输赢
    winLoss = Column(Integer(), default=0, nullable=False)              # 总输赢
    probetRate = Column(Float(), default=0, nullable=False)             # 电竞平台费率
    pingboRate = Column(Float(), default=0, nullable=False)             # 平博平台费率
    probetCost = Column(Integer(), default=0, nullable=False)           # 电竞平台费
    pingboCost = Column(Integer(), default=0, nullable=False)           # 平博平台费
    platformCost = Column(Integer(), default=0, nullable=False)         # 平台费
    depositDrawingCost = Column(Integer(), default=0, nullable=False)   # 存提手续费
    backWater = Column(Integer(), default=0, nullable=False)            # 反水
    bonus = Column(Integer(), default=0, nullable=False)                # 活动奖金
    water = Column(Integer(), default=0, nullable=True)                 # 流水
    netProfit = Column(Integer(), default=0, nullable=False)            # 净利润
    preBalance = Column(Integer(),default=0,nullable=False)             # 上月结余
    balance = Column(Integer(),default=0,nullable=False)                # 本月结余
    commissionRate = Column(Float(), default=0, nullable=False)         # 佣金比
    commission = Column(Integer(), default=0, nullable=False)           # 佣金
    status = Column(Integer(), default=0, nullable=False)               # 佣金状态   0：已发放  1：未发放
    handleTime=Column(Integer(), default=0, nullable=True)              # 发放时间
    reviewer = Column(String(32), default="", nullable=True)            # 审核人（发放佣金用）
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

class DomainName(Base):
    # 域名
    __tablename__ = 'dj_domain'
    domainId = Column(String(64), primary_key=True)
    domainName = Column(String(255), default="", nullable=True)
    # domainName = Column(String(255), primary_key=True)
    domainType = Column(String(64),nullable=True)
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

class ActiveData(Base):
    __tablename__ = 'dj_active'
    accountId = Column(String(64), primary_key=True)
    dictActiveItem = Column(JSON,  default="",nullable=False)
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

class material(Base,BaseModel):
    # 推广素材
    __tablename__ = 'dj_material'
    imageId = Column(String(64), primary_key=True)
    image_url = Column(String(1024), default='', nullable=False)
    imageSize = Column(String(128),nullable=True)
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

class applyForAgent(Base):
    # 代理申请表
    __tablename__ = 'dj_agent_apply'
    agentId = Column(String(64), primary_key=True)
    applyTime = Column(Integer(), default=0, nullable=False)
    qq = Column(String(64),nullable=True)
    website = Column(String(255), default="", nullable=True)
    introduction = Column(Text(length=65536), default="", nullable=True)
    status = Column(SmallInteger(), default=0, nullable=False)
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }


tb_admin = Base.metadata.tables["dj_admin_account"]
tb_role=Base.metadata.tables["dj_admin_role"]
tb_role_action=Base.metadata.tables["dj_admin_role_action"]
tb_action=Base.metadata.tables["dj_admin_action"]
tb_dj_account=Base.metadata.tables["dj_account"]
tb_banner=Base.metadata.tables["dj_banner"]
tb_active=Base.metadata.tables["dj_active"]
tb_material=Base.metadata.tables["dj_material"]
tb_applyForAgent=Base.metadata.tables["dj_agent_apply"]
tb_agent_commission=Base.metadata.tables["dj_agent_commission"]
tb_pinbo_wagers=Base.metadata.tables["dj_pinbo_wagers"]

if __name__ == '__main__':
    from gmweb.utils.db_tools import objEngine
    # from gmweb.utils.db_tools import session
    metadata = MetaData(objEngine)
    #创建表
    #msgTbl = Base.metadata.tables["dj_all_msg"]
    Base.metadata.drop_all(objEngine)
    Base.metadata.create_all(objEngine)
    # print(dir(Base))
    # print(dir(Base.metadata.tables["dj_bet"]))
    # print(type(Base.metadata.tables["dj_bet"]))
    #from dbsvr.logic.bet_flush import tbl
    #print(type(tbl))
    #print(BetInfo)


    # role=Role(role_name='系统管理员')
    # session.add(role)
    # session.commit()
    # account = session.query(Administer).filter(Administer.accountId=='admin').first()

    #
    # print(account.id)
    #hash_pwd=generate_password_hash('123456')
    #print(hash_pwd)

    # account=Administer()
    # account.accountId='admin'
    # account.password_hash='123456'
    # account.role_id='1'
    # session.add(account)
    # session.commit()
    # session.close()
    # a=session.query(Administer).order_by(Administer.id)
