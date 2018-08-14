from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, MetaData, Table, ForeignKey, BigInteger, Text, SmallInteger, Float, \
    PickleType, DECIMAL,JSON,DateTime


Base=declarative_base()

class AdminActionBill(Base):
    # 管理员操作日志模型类
    __tablename__='dj_admin_action_bill'

    id=Column(Integer(),primary_key=True,autoincrement=True)
    accountId = Column(String(32),default='',)
    action = Column(String(120),default='')
    actionTime = Column(Integer(),default=0)
    actionDetail = Column(String(1024),default='')
    actionIp = Column(String(120),default='')
    actionMethod = Column(String(120),default='')
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

    @staticmethod
    def getSqlObj(dictBill:dict):
        tbl = Base.metadata.tables["dj_admin_action_bill"]
        objSql = tbl.insert().values(
            accountId=dictBill["accountId"],
            action=dictBill["action"],
            actionTime=dictBill["actionTime"],
            actionDetail=dictBill["actionDetail"],
            actionIp=dictBill['actionIp'],
            actionMethod=dictBill['actionMethod'],
        )
        return objSql

class ProbetBetBill(Base):
    #竞猜注单日志模型类
    __tablename__='dj_betbill'

    id=Column(Integer(), primary_key=True,autoincrement=True)
    accountId=Column(String(32), default="")
    agentId=Column(String(32), default="")
    matchId=Column(String(45), default="")
    guessId=Column(String(45), default="")
    playType=Column(String(45), default="")
    roundNum=Column(Integer(),default=0)
    supportType=Column(String(45), default="")
    betCoinNum=Column(Integer(), default=0)#竞猜金额
    betTime=Column(Integer(), default=0)
    coinBeforeBet=Column(BigInteger(), default=0)
    coinAfterBet=Column(BigInteger(), default=0)
    guessLevelBeforeBet=Column(Integer(), default=0)
    guessLevelAfterBet=Column(Integer(), default=0)
    guessExpBeforeBet=Column(Integer(), default=0)
    guessExpAfterBet=Column(Integer(),default=0)
    projectType=Column(String(12), default="")
    betHisUId=Column(String(45), default="")
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

    @staticmethod
    def getSqlObj(dictBill: dict):
        tbl = Base.metadata.tables["dj_betbill"]
        objSql = tbl.insert().values(
            accountId=dictBill["accountId"],
            matchId=dictBill["matchId"],
            guessId=dictBill["guessId"],
            playType=dictBill["playType"],
            roundNum=dictBill["roundNum"],
            supportType=dictBill["supportType"],
            betCoinNum=dictBill["betCoinNum"],
            betTime=dictBill["betTime"],
            coinBeforeBet=dictBill["coinBeforeBet"],
            coinAfterBet=dictBill["coinAfterBet"],
            guessLevelBeforeBet=dictBill["guessLevelBeforeBet"],
            guessLevelAfterBet=dictBill["guessLevelAfterBet"],
            guessExpBeforeBet=dictBill["guessExpBeforeBet"],
            guessExpAfterBet=dictBill["guessExpAfterBet"],
            projectType=dictBill["projectType"],
            betHisUId=dictBill["betHisUId"],
            agentId=dictBill['agentId']
        )

        return objSql

class BetResultBill(Base):
    #注单结果日志模型类
    __tablename__='dj_betresultbill'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    accountId = Column(String(32), default="")
    agentId = Column(String(32), default="")
    matchType=Column(String(46),default='')
    matchId=Column(String(45), default="")
    guessName=Column(String(45),default='')
    guessId=Column(String(45), default="")
    playType=Column(String(45), default="")
    roundNum=Column(Integer(), default=0)
    supportType=Column(String(45), default="")
    rate=Column(Float(), default=0)
    betCoinNum=Column(Integer(), default=0)
    coinBeforeWin=Column(Integer(), default=0)
    coinAfterWin=Column(Integer(), default=0)
    winCoin=Column(Integer(), default=0)
    projectType=Column(String(12), default="")
    resultTime=Column(Integer(), default=0)
    betTime=Column(Integer(), default=0)
    betResult=Column(String(255), default="")
    vipLevel=Column(Integer(),default=0)
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

    @staticmethod
    def getSqlObj(dictBill: dict):
        tbl = Base.metadata.tables["dj_betresultbill"]
        objSql = tbl.insert().values(
            accountId=dictBill["accountId"],
            matchId=dictBill["matchId"],
            guessName=dictBill['guessName'],
            matchType=dictBill['matchType'],
            guessId=dictBill["guessId"],
            playType=dictBill["playType"],
            roundNum=dictBill["roundNum"],
            supportType=dictBill["supportType"],  # 支持的类型
            rate=dictBill['rate'],
            betCoinNum=dictBill["betCoinNum"],
            coinBeforeWin=dictBill["coinBeforeWin"],
            coinAfterWin=dictBill["coinAfterWin"],
            projectType=dictBill["projectType"],
            winCoin=dictBill['winCoin'],  # 赢的钱
            resultTime=dictBill["resultTime"],
            betTime=dictBill["betTime"],
            betResult=dictBill["betResult"],
            agentId=dictBill['agentId'],
            vipLevel=dictBill['vipLevel']
        )

        return objSql

class FilePos(Base):
    #文件扫描模型类
    __tablename__ = 'dj_filepos'

    hostName=Column(String(45), primary_key=True)
    fileName=Column(String(128), default="")
    seekPos=Column(Integer(), default=0)
    lastLogTime=Column(DateTime(), default="")
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

    @staticmethod
    def getInsertSqlObj(hostName, fileName, seekPos, lastLogTime):
        tbl = Base.metadata.tables["dj_filepos"]
        objSql = tbl.insert().values(
            hostName=hostName,
            fileName=fileName,
            seekPos=seekPos,
            lastLogTime=datetime.fromtimestamp(lastLogTime)
        )

        return objSql

    @staticmethod
    def getSelectSqlObj(hostName):
        tbl = Base.metadata.tables["dj_filepos"]
        objSql = tbl.select().where(tbl.c.hostName == hostName)

        return objSql

    @staticmethod
    def getUpdateSqlObj(hostName, fileName, seekPos, lastLogTime):
        tbl = Base.metadata.tables["dj_filepos"]
        objSql = tbl.update().where(tbl.c.hostName == hostName).values(
            fileName=fileName,
            seekPos=seekPos,
            lastLogTime=datetime.fromtimestamp(lastLogTime)
        )

        return objSql

class LoginBill(Base):
    #登录日志模型类
    __tablename__='dj_loginbill'

    id=Column(Integer(), primary_key=True,autoincrement=True)
    accountId=Column(String(32), default="")
    loginTime=Column(Integer(), default=0)
    loginDevice=Column(String(45), default="")
    loginIp=Column(String(45), default="")
    coin=Column(BigInteger(), default=0)
    vipLevel=Column(Integer(), default=0)
    vipExp=Column(Integer(), default=0)
    agentId=Column(String(32), default='')
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

    @staticmethod
    def getSqlObj(dictBill: dict):
        tbl = Base.metadata.tables["dj_loginbill"]
        objSql = tbl.insert().values(
            accountId=dictBill["accountId"],
            loginTime=dictBill["loginTime"],
            loginDevice=dictBill["loginDevice"],
            loginIp=dictBill["loginIp"],
            coin=dictBill["coin"],
            vipLevel=dictBill["vipLevel"],
            vipExp=dictBill["vipExp"],
            agentId=dictBill['agentId']
        )

        return objSql

class PayBill(Base):
    #支付日志模型类
    __tablename__ = 'dj_paybill'

    orderId=Column(String(128), primary_key=True)
    accountId=Column(String(32), default="")
    payTime=Column(Integer(), default=0)
    payIp=Column(String(32), default="")
    payCoin=Column(Integer(), default=0)
    payChannel=Column(String(45), default="")
    orderState=Column(Integer(), default=0)
    firstPayCoin=Column(Integer(),default=0)
    agentId=Column(String(32), default="")
    firstPayTime=Column(Integer(),default=0)
    thirdPayOrder=Column(String(128),default="")
    thirdPayName = Column(String(64), default="")
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

    @staticmethod
    def getSqlObj(dictBill: dict):
        tbl = Base.metadata.tables["dj_paybill"]
        objSql = tbl.insert().values(
            orderId=dictBill["orderId"],
            accountId=dictBill["accountId"],
            payTime=dictBill["payTime"],
            payIp=dictBill["payIp"],
            payCoin=dictBill["payCoin"],
            payChannel=dictBill["payChannel"],
            orderState=dictBill["orderState"],
            firstPayCoin=dictBill['firstPayCoin'],
            agentId=dictBill['agentId'],
            #firstPayTime=dictBill['firstPayTime'],
            thirdPayOrder=dictBill['thirdPayOrder'],
            thirdPayName=dictBill['thirdPayName'],
        )

        return objSql

class PingboBetBill(Base):
    #平博注单模型类
    __tablename__ = 'dj_pingbobetbill'
    wagerId=Column(Integer(), default = 0,primary_key=True)
    sport=Column(String(45), default = "")
    league=Column(String(45), default = "")
    eventName=Column(String(256), default = '')
    homeTeam=Column(String(45), default = "")
    awayTeam=Column(String(45), default = "")
    selection=Column(String(45), default = 0)
    oddsFormat=Column(Integer(), default = 0)
    odds=Column(Float(), default = 0)
    stake=Column(Float(), default = 0)
    betType=Column(SmallInteger(), default = 0)
    eventDateFm=Column(Integer(), default = '')
    result=Column(String(32), default = '')
    status=Column(String(32), default = '')
    toWin=Column(String(32), default = '')
    toRisk=Column(String(32), default = '')
    winLoss=Column(Float(), default = '')
    currencyCode=Column(String(32), default = '')
    userCode=Column(String(45), default = '')
    loginId=Column(String(45), default = '')
    product=Column(String(32), default = '')
    wagerDateFm=Column(Integer(), default = 0)
    agentId=Column(String(32), default = '')
    settleDateFm=Column(Integer(), default = 0)
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

    @staticmethod
    def getUpdateSql(dictBill:dict):
        from lib.timehelp.timeHelp import strToTimestamp,str2TimeStamp

        tbl = Base.metadata.tables["dj_pingbobetbill"]
        objSql = tbl.update().where(tbl.c.wagerId==dictBill['wagerId']).values(
            wagerId=dictBill['wagerId'],
            sport=dictBill['sport'],
            league=dictBill["league"],
            eventName=dictBill["eventName"],
            homeTeam=dictBill["homeTeam"],
            awayTeam=dictBill["awayTeam"],
            selection=dictBill['selection'],
            oddsFormat=dictBill["oddsFormat"],
            odds=dictBill["odds"],
            stake=dictBill["stake"],
            betType=dictBill["betType"],
            eventDateFm=str2TimeStamp(dictBill["eventDateFm"]),
            result=dictBill['result'],
            settleDateFm=0 if dictBill['settleDateFm'] is None or dictBill['settleDateFm'] == '' else strToTimestamp(
                dictBill['settleDateFm']),
            status=dictBill["status"],
            toWin=dictBill["toWin"],
            toRisk=dictBill["toRisk"],
            winLoss=dictBill['winLoss'],
            currencyCode=dictBill['currencyCode'],
            userCode=dictBill['userCode'],
            loginId=dictBill['loginId'],
            product=dictBill['product'],
            wagerDateFm=strToTimestamp(dictBill['wagerDateFm']),
            agentId=dictBill['agentId']
        )

        return objSql

    @staticmethod
    def getSqlObj(dictBill: dict):
        from lib.timehelp.timeHelp import strToTimestamp,str2TimeStamp
        tbl = Base.metadata.tables["dj_pingbobetbill"]
        objSql = tbl.insert().values(
            wagerId=dictBill['wagerId'],
            sport=dictBill['sport'],
            league=dictBill["league"],
            eventName=dictBill["eventName"],
            homeTeam=dictBill["homeTeam"],
            awayTeam=dictBill["awayTeam"],
            selection=dictBill['selection'],
            oddsFormat=dictBill["oddsFormat"],
            odds=dictBill["odds"],
            stake=dictBill["stake"],
            betType=dictBill["betType"],
            eventDateFm=str2TimeStamp(dictBill["eventDateFm"]),
            result=dictBill['result'],
            settleDateFm=0 if dictBill['settleDateFm'] is None or dictBill['settleDateFm'] == '' else strToTimestamp(
                dictBill['settleDateFm']),
            status=dictBill["status"],
            toWin=dictBill["toWin"],
            toRisk=dictBill["toRisk"],
            winLoss=dictBill['winLoss'],
            currencyCode=dictBill['currencyCode'],
            userCode=dictBill['userCode'],
            loginId=dictBill['loginId'],
            product=dictBill['product'],
            wagerDateFm=strToTimestamp(dictBill['wagerDateFm']),
            agentId=dictBill['agentId']
        )

        return objSql

class RegisterBill(Base):
    #注册日志模型类
    __tablename__ = 'dj_regbill'

    id=Column(Integer(), primary_key = True, autoincrement = True)
    accountId=Column(String(32), default = "")
    regTime=Column(String(45), default = "")
    regIp=Column(String(45), default = "")
    channel=Column(Integer(), default = 0)
    regDevice=Column(String(45), default = "")
    agentId=Column(String(32), default = '')
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

    @staticmethod
    def getSqlObj(dictBill: dict):
        tbl = Base.metadata.tables["dj_regbill"]
        objSql = tbl.insert().values(
            accountId=dictBill["accountId"],
            regTime=dictBill["regTime"],
            regIp=dictBill["regIp"],
            channel=dictBill.get("channel", ""),  # 渠道
            regDevice=dictBill["regDevice"],
            agentId=dictBill.get('agentId', '')  # 代理
        )

        return objSql

class WihtDrawalBill(Base):
    #提款日志模型类
    __tablename__ = 'dj_withdrawalbill'

    orderId=Column(String(128), primary_key=True)
    accountId=Column(String(32), default="")
    withdrawalTime=Column(Integer(), default=0)
    withdrawalIp=Column(String(32), default="")
    withdrawalCoin=Column(Integer(), default=0)
    cardNum=Column(String(20), default="")
    orderState=Column(Integer(), default=0)
    agentId=Column(String(32),default='')
    userType=Column(SmallInteger(),default=1)
    bankOrderId=Column(String(128),default='')  #提款时银行流水号
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

    @staticmethod
    def getSqlObj(dictBill: dict):
        tbl = Base.metadata.tables["dj_withdrawalbill"]
        objSql = tbl.insert().values(
            orderId=dictBill["orderId"],
            accountId=dictBill["accountId"],
            withdrawalTime=dictBill["withdrawalTime"],
            withdrawalIp=dictBill["withdrawalIp"],
            withdrawalCoin=dictBill["withdrawalCoin"],
            cardNum=dictBill["cardNum"],
            orderState=dictBill["orderState"],
            agentId=dictBill['agentId'],
            userType=dictBill['userType'],
            bankOrderId=dictBill['bankOrderId'],
        )

        return objSql

class ShabaBetBill(Base):
    #沙巴日志模型类
    __tablename__ = 'dj_shababetbill'

    transId=Column(BigInteger(),default=0,primary_key=True)
    sportType=Column(Integer(), default=0)
    leagueId=Column(Integer(), default=0)
    homeId=Column(Integer(), default=0)
    awayId=Column(Integer(), default=0)
    betTeam=Column(String(45), default='')
    oddsType=Column(SmallInteger(), default=0)
    odds=Column(Float(), default=0)
    stake=Column(Float(), default=0)
    betType=Column(SmallInteger(),default=0)
    ticketStatus=Column(String(10),default='')
    winLostAmount=Column(Float(),default='')
    currency=Column(SmallInteger(),default=0)
    vendorMemberId=Column(String(50),default='')
    transActionTime=Column(Integer(),default=0)
    agentId=Column(String(32),default='')
    winLostDateTime=Column(Integer(),default=0)
    operatorId=Column(String(50),default='')
    baStatus=Column(String(5),default='')
    betTag=Column(String(500),default='')
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

    @staticmethod
    def getSqlObj(dictBill: dict):
        tbl = Base.metadata.tables["dj_shababetbill"]
        from lib.timehelp.timeHelp import strToTimestamp
        objSql = tbl.insert().values(
            vendorMemberId=dictBill["vendorMember_id"],
            transId=dictBill['trans_id'],
            sportType=dictBill['sport_type'],
            leagueId=dictBill["league_id"],
            betTag=dictBill["bet_tag"],
            homeId=dictBill["home_id"],
            awayId=dictBill["away_id"],
            betTeam=dictBill['bet_team'],
            oddsType=dictBill["odds_type"],
            odds=dictBill["odds"],
            stake=dictBill["stake"],
            betType=dictBill["bet_type"],
            transActionTime=strToTimestamp(dictBill["transaction_time"]),
            winLostDateTime=strToTimestamp(dictBill['winlost_datetime']),
            ticketStatus=dictBill["ticket_status"],
            winLostAmount=dictBill["winlost_amount"],
            currency=dictBill['currency'],
            agentId=dictBill['agentId'],
            operatorId=dictBill['operator_id'],
            baStatus=dictBill['ba_status'],
        )

        return objSql


class OnlineBill(Base):
    #在线用户模型类
    __tablename__ = 'dj_onlinebill'

    groupId=Column(Integer(), primary_key=True, autoincrement=False)
    onlineCount=Column(Integer(), default=0)
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }

    @staticmethod
    def getInsertSqlObj(dictBill: dict):
        tbl = Base.metadata.tables["dj_onlinebill"]
        objSql = tbl.insert().values(
            groupId=dictBill["groupId"],
            onlineCount=dictBill["onlineCount"],
        )

        return objSql

    @staticmethod
    def getSelectSqlObj(dictBill: dict):
        tbl = Base.metadata.tables["dj_onlinebill"]
        objSql = tbl.select().where(tbl.c.groupId == dictBill['groupId'])

        return objSql

    @staticmethod
    def getUpdateSqlObj(dictBill: dict):
        tbl = Base.metadata.tables["dj_onlinebill"]
        objSql = tbl.update().where(tbl.c.groupId == dictBill['groupId']).values(
            onlineCount=dictBill["onlineCount"],
        )

        return objSql

tb_dj_admin_action_bill = Base.metadata.tables["dj_admin_action_bill"]