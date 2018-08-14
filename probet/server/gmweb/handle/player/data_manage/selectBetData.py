import asyncio
import json
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.tools import token_required, permission_required
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow
from logic.logicmgr.checkParamValid import checkIsInt

class cData1():
    def __init__(self):
        self.loginCount=0       #登录数
        self.regCount=0         #新增数
        self.betCount=0         #投注人数
        self.newBetCount=0      #新增投注人数
        self.handicapWater=0    #盘口抽水
        self.totalWater=0       #总流水
        self.validWater=0       #有效流水
        self.totalBetCount=0    #总投注笔数
        self.avgBetCount=0      #平均投注笔数
        self.returnAwardCoin=0  #返奖金额
        self.betWinRate=0       #注单中奖率
        self.profitLoss = 0     # 盈亏
        self.profitLossRatio = 0# 盈亏比

class cData2():
    def __init__(self):
        self.gameName=''        #游戏名
        self.handicapWater=0    #盘口抽水
        self.betUsers=0         #注单用户数
        self.betCoin=0          #投注金额
        self.betCount=0         #注单数
        self.avgBetCount=0      #平均注单数


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.handicapData = []
        self.overAllData=""

@token_required
@permission_required('投注信息查询')
@asyncio.coroutine
def handleHttp(request: dict):
    """根据时间，渠道获取投注信息"""
    channel = request.get('channel', '')
    startTime = request.get('startTime', 0)
    endTime = request.get('endTime', 0)

    objRep = cResp()

    if not all([startTime,endTime]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    if (not checkIsInt(startTime)) or (not checkIsInt(endTime)):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        conn=classSqlBaseMgr.getInstance(instanceName='probet_oss')
        over_all_data=cData1()
        #登录用户数
        login_count_sql="select count(DISTINCT(accountId)) from dj_loginbill WHERE loginTime BETWEEN {} AND {} ".format(startTime,endTime)
        #新增用户数
        new_reg_count_sql="select count(id) from dj_regbill WHERE regTime BETWEEN {} AND {} ".format(startTime,endTime)
        #投注用户数 总投注笔数 总流水 返奖金额
        bet_count_sql="select count(DISTINCT(accountId)),COUNT(id),SUM(betCoinNum),SUM(winCoin) from dj_betresultbill WHERE resultTime BETWEEN {} AND {} ".format(startTime,endTime)
        #1.查询时间之前下过注的账号
        before_users_sql="SELECT DISTINCT(accountId) FROM dj_betresultbill WHERE resultTime<{} ".format(startTime)
        #2.获取查询开始时间之后的所有用户
        after_users_sql="select accountId from dj_regbill WHERE accountId not in {}"
        #有效流水
        valid_water_sql="select sum(betCoinNum) from dj_betresultbill WHERE rate>=1.5 AND resultTime BETWEEN {} AND {} ".format(startTime,endTime)
        #中奖注单数
        win_bet_count_sql="select count(id) from dj_betresultbill WHERE winCoin>0"
        # 获取所有盘口数据
        gameNames = []
        sql = "select DISTINCT(GuessName) from dj_betresultbill"
        listRest = yield from conn._exeCute(sql)
        names = yield from listRest.fetchall()
        for x in names:
            gameNames.append(x[0])
        gameNames.append('平博')
        #todo
        if channel:
            for game in gameNames:
                handicap_data=cData2()
                handicap_data.gameName=game
                # 下注人数，总下注额，注单数
                handicap_sql="select COUNT(DISTINCT(accountId)),sum(betCoinNum),COUNT(id) from dj_betresultbill WHERE agentId='{}' AND resultTime BETWEEN {} AND {} AND guessName='{}' ".format(
                    channel,startTime,endTime,game)
                if game=='平博':
                    handicap_sql="select COUNT(DISTINCT(loginId)),sum(toRisk),COUNT(wagerId) from dj_pingbobetbill WHERE agentId='{}' AND wagerDateFm BETWEEN {} AND {} ".format(channel,startTime,endTime)
                listRest=yield from conn._exeCute(handicap_sql)
                result=yield from listRest.fetchone()
                handicap_data.betUsers=result[0]
                handicap_data.betCoin=0 if result[1] is None else int(result[1])/100
                handicap_data.betCount=result[2]
                handicap_data.avgBetCount=0 if handicap_data.betUsers==0 else handicap_data.betCount/handicap_data.betUsers
                # todo 盘口抽水
                handicap_data.handicapWater = handicap_data.betCoin * 0.15
                objRep.handicapData.append(handicap_data)

            login_count_sql=login_count_sql+" AND agentId='{}' ".format(channel)
            new_reg_count_sql=new_reg_count_sql+" AND agentId='{}' ".format(channel)
            bet_count_sql=bet_count_sql+" AND agentId='{}' ".format(channel)
            before_users_sql=before_users_sql+" AND agentId='{}' ".format(channel)
            after_users_sql=after_users_sql+" AND agentId='"+channel+"' "
            valid_water_sql=valid_water_sql+" AND agentId='{}' ".format(channel)
            win_bet_count_sql=win_bet_count_sql+" AND agentId='{}' ".format(channel)
        else:
            for game in gameNames:
                handicap_data = cData2()
                handicap_data.gameName = game
                # 下注人数，总下注额，注单数
                handicap_sql = "select COUNT(DISTINCT(accountId)),sum(betCoinNum),COUNT(id) from dj_betresultbill WHERE resultTime BETWEEN {} AND {} AND guessName='{}' ".format(
                    startTime, endTime,game)
                if game == '平博':
                    handicap_sql = "select COUNT(DISTINCT(loginId)),sum(toRisk),COUNT(wagerId) from dj_pingbobetbill WHERE wagerDateFm BETWEEN {} AND {} ".format(
                    startTime, endTime)
                listRest = yield from conn._exeCute(handicap_sql)
                result = yield from listRest.fetchone()
                handicap_data.betUsers = result[0]
                handicap_data.betCoin = 0 if result[1] is None else int(result[1])
                handicap_data.betCount = result[2]
                handicap_data.avgBetCount = 0 if handicap_data.betUsers == 0 else round(handicap_data.betCount / handicap_data.betUsers,2)
                #todo 盘口抽水
                handicap_data.handicapWater=round(handicap_data.betCoin*0.15,2)
                objRep.handicapData.append(handicap_data)

        listRest=yield from conn._exeCute(login_count_sql)
        login_count=yield from listRest.fetchone()
        over_all_data.loginCount=login_count[0]

        listRest = yield from conn._exeCute(new_reg_count_sql)
        reg_count = yield from listRest.fetchone()
        over_all_data.regCount = reg_count[0]

        listRest = yield from conn._exeCute(bet_count_sql)
        bet_count = yield from listRest.fetchone()
        over_all_data.betCount = bet_count[0]
        over_all_data.totalBetCount=bet_count[1]
        over_all_data.totalWater=0 if bet_count[2] is None else int(bet_count[2])/100
        over_all_data.returnAwardCoin=0 if bet_count[3] is None else int(bet_count[3])/100

        listRest = yield from conn._exeCute(before_users_sql)
        before_users = yield from listRest.fetchall()
        before_accountIds=[]
        for x in before_users:
            before_accountIds.append(x[0])
        if len(before_accountIds)==0:
            #todo 可以优化
            after_users_sql = "select accountId from dj_betresultbill WHERE resultTime BETWEEN {} AND {} ".format(startTime,endTime)
            if channel:
                after_users_sql="select accountId from dj_betresultbill WHERE agentId='{}' AND resultTime BETWEEN {} AND {} ".format(channel,startTime,endTime)
        elif len(before_accountIds)==1:
            before_accountIds=str(tuple(before_accountIds)).replace(r',','')
            after_users_sql = after_users_sql.format(before_accountIds)
        else:
            before_accountIds=tuple(before_accountIds)
            after_users_sql=after_users_sql.format(before_accountIds)

        listRest=yield from conn._exeCute(after_users_sql)
        after_users=yield from listRest.fetchall()
        after_accountIds=[]
        for x in after_users:
            after_accountIds.append(x[0])
        if len(after_accountIds)==0:
            over_all_data.newBetCount=0
        elif len(after_accountIds)==1:
            after_accountIds=str(tuple(after_accountIds)).replace(r',','')
            # 新增投注用户数
            new_bet_count_sql = "select COUNT(accountId) from dj_betresultbill WHERE accountId in {} AND resultTime BETWEEN {} AND {}".format(
                after_accountIds, startTime, endTime)
            listRest = yield from conn._exeCute(new_bet_count_sql)
            new_bet_count = yield from listRest.fetchone()
            over_all_data.newBetCount = new_bet_count[0]
        else:
            after_accountIds=tuple(after_accountIds)
            # 新增投注用户数
            new_bet_count_sql = "select COUNT(accountId) from dj_betresultbill WHERE accountId in {} AND resultTime BETWEEN {} AND {}".format(after_accountIds,startTime,endTime)
            listRest=yield from conn._exeCute(new_bet_count_sql)
            new_bet_count=yield from listRest.fetchone()
            over_all_data.newBetCount=new_bet_count[0]

        listRest = yield from conn._exeCute(valid_water_sql)
        valid_water = yield from listRest.fetchone()
        over_all_data.validWater =0 if valid_water[0] is None else int(valid_water[0])/100

        listRest = yield from conn._exeCute(win_bet_count_sql)
        win_bet_count = yield from listRest.fetchone()
        win_bet_count = win_bet_count[0]

        #todo 盘口抽水
        over_all_data.handicapWater=over_all_data.totalWater*0.15
        #平均投注笔数
        over_all_data.avgBetCount=0 if over_all_data.betCount==0 else round(over_all_data.totalBetCount/over_all_data.betCount,2)
        #盈亏
        over_all_data.profitLoss=over_all_data.totalWater-over_all_data.returnAwardCoin
        #盈亏比
        over_all_data.profitLossRatio=0 if over_all_data.totalWater==0 else "%.3f"%round(over_all_data.profitLoss/over_all_data.totalWater,3)
        #注单中奖率
        over_all_data.betWinRate=0 if over_all_data.totalBetCount==0 else win_bet_count/over_all_data.totalBetCount
        objRep.overAllData=over_all_data

        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "投注数据查询",
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionDetail': "投注数据查询",
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)
