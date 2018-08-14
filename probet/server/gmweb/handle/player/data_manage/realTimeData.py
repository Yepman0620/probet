import asyncio
import json
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.getPingboValidWater import getPingboValidWaterByParams
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from logic.logicmgr.checkParamValid import checkIsInt
from lib.timehelp.timeHelp import getTimeOClockOfToday, getNow, monthStartTimestamp


class cData1():
    def __init__(self):
        self.todayLogin=0       #今日登录数
        self.todayNew=0         #今日新增
        self.totalReg=0         #总注册
        self.todayAward=0              #今日派奖
        self.todayRecharge=0    #今日充值
        self.RechargeCount=0    #充值人数
        self.todayPumping=0     #今日抽水
        self.todayWater=0         #今日流水
        self.todayValidWater=0      #今日有效流水
        self.withdrawal=0       #提款
        self.winLoss=0       #盈利
        self.totalRecharge=0  #总充值
        self.newRecharge=0    #新增充值用户数
        self.newRechargeCoin=0  # 新增充值总额

class cData2():
    def __init__(self):
        self.agentCount=0       #代理总数
        self.agentNew=0         #新增代理
        self.vipNew=0           #新增会员
        self.vipWinLoss=0       #会员总输赢
        self.withdrawal=0       #提款
        self.winLoss=0          #盈亏

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.agentData = {}
        self.operationData={}

@token_required
@permission_required('实时数据查询')
@asyncio.coroutine
def handleHttp(request: dict):
    """获取实时数据"""
    days=request.get('days',0)
    startTime = getTimeOClockOfToday()
    endTime = getNow()

    objRep = cResp()

    if not checkIsInt(days):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    if days not in [0,3,5,7,30]:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    if days:
        if days==30:
            startTime=monthStartTimestamp()
        else:
            startTime=startTime-days*24*3600
    #运营实时数据sql
    reg_count_sql="select count(id) from dj_regbill"
    today_login_sql="select count(DISTINCT(accountId)) from dj_loginbill WHERE loginTime BETWEEN {} AND {}".format(startTime,endTime)
    today_new_sql="select count(id) from dj_regbill where regTime BETWEEN {} AND {}".format(startTime,endTime)
    recharge_sql="select count(DISTINCT(accountId)) from dj_paybill"
    today_recharge_sql="select count(DISTINCT(accountId)) from dj_paybill WHERE payTime BETWEEN {} AND {}".format(startTime,endTime)
    today_pro_water_award_sql="select sum(betCoinNum),sum(winCoin) from dj_betresultbill WHERE resultTime BETWEEN {} AND {}".format(startTime,endTime)
    today_pin_water_award_sql="select sum(toRisk),sum(CASE WHEN winLoss>0 THEN winLoss ELSE 0 END) from dj_pingbobetbill WHERE wagerDateFm BETWEEN {} AND {} AND status='SETTLED'".format(startTime,endTime)
    pro_valid_water_sql="select sum(betCoinNum) from dj_betresultbill WHERE resultTime BETWEEN {} AND {} AND rate>=1.5".format(startTime,endTime)
    withdrawal_sql="select sum(withdrawalCoin) from dj_withdrawalbill WHERE withdrawalTime BETWEEN {} AND {}".format(startTime,endTime)
    total_recharge_sql="select sum(payCoin) from dj_paybill WHERE payTime BETWEEN {} AND {} ".format(startTime,endTime)
    new_recharge_sql="select DISTINCT(accountId) from dj_paybill WHERE accountId not IN (SELECT accountId from dj_paybill WHERE payTime<{}) AND payTime BETWEEN {} AND {}".format(startTime,startTime,endTime)
    new_recharge_coin_sql="select sum(payCoin) from dj_paybill WHERE accountId IN ("+new_recharge_sql+") and payTime between {} and {} ".format(startTime,endTime)

    #代理实时数据sql
    agent_count_sql="select count(agentId) from dj_agent"
    agent_new_sql="select count(agentId) from dj_agent WHERE regTime BETWEEN {} AND {}".format(startTime,endTime)
    today_new_offline_sql="select count(accountId) from dj_regbill WHERE agentId!='' AND regTime BETWEEN {} AND {}".format(startTime,endTime)
    #线下总输赢
    vip_win_loss_sql="select sum(betCoinNum),sum(winCoin) from dj_betresultbill WHERE agentId!='' AND resultTime BETWEEN {} AND {}".format(startTime,endTime)
    agent_bet_award_sql="select sum(betCoinNum),sum(winCoin) from dj_betresultbill WHERE agentId!='' AND resultTime BETWEEN {} AND {}".format(startTime,endTime)
    agent_withdrawal_sql="select sum(withdrawalCoin) from dj_withdrawalbill WHERE userType=2 AND withdrawalTime BETWEEN {} AND {}".format(startTime,endTime)


    try:
        operation_data=cData1()
        agent_data=cData2()
        with (yield from classSqlBaseMgr.getInstance(instanceName='probet_oss').objDbMysqlMgr) as conn:
            #注册总数
            reg_count=yield from conn.execute(reg_count_sql)
            reg_total_count=yield from reg_count.fetchone()
            operation_data.totalReg=reg_total_count[0]
            #今日登录数
            today_login=yield from conn.execute(today_login_sql)
            login_count=yield from today_login.fetchone()
            operation_data.todayLogin=login_count[0]
            #今日新增数
            today_reg=yield from conn.execute(today_new_sql)
            new_reg=yield from today_reg.fetchone()
            operation_data.todayNew=new_reg[0]
            #充值总数
            recharge_count=yield from conn.execute(recharge_sql)
            total_recharge=yield from recharge_count.fetchone()
            operation_data.RechargeCount=total_recharge[0]
            #今日充值数
            today_recharge_count=yield from conn.execute(today_recharge_sql)
            today_recharge=yield from today_recharge_count.fetchone()
            operation_data.todayRecharge=today_recharge[0]
            #今日流水：平博今日流水+Probet流水
            today_pro_water_award=yield from conn.execute(today_pro_water_award_sql)
            pro_water_award=yield from today_pro_water_award.fetchone()
            today_pin_water_award=yield from conn.execute(today_pin_water_award_sql)
            pin_water_award=yield from today_pin_water_award.fetchone()
            pin_water=0 if pin_water_award[0] is None else pin_water_award[0]
            pro_water=0 if pro_water_award[0] is None else int(pro_water_award[0])/100
            operation_data.todayWater=round(pin_water+pro_water,2)
            #今日有效流水：平博有效流水+Probet有效流水 欧赔+亚赔
            pinValidWater=yield from getPingboValidWaterByParams(loginIds=None,startTime=startTime,endTime=endTime)

            today_pro_valid_water=yield from conn.execute(pro_valid_water_sql)
            pro_valid_water=yield from today_pro_valid_water.fetchone()
            proValidWater=0 if pro_valid_water[0] is None else int(pro_valid_water[0])/100
            operation_data.todayValidWater=round(pinValidWater+proValidWater,2)
            #今日抽水：总流水*0.15   todo
            operation_data.todayPumping=round(operation_data.todayWater*0.15,2)
            #总充值数
            total_recharge_ret=yield from conn.execute(total_recharge_sql)
            totalRechargeRes=yield from total_recharge_ret.fetchone()
            operation_data.totalRecharge=0 if totalRechargeRes[0] is None else int(totalRechargeRes[0])/100
            #新增充值人数
            new_recharge_ret=yield from conn.execute(new_recharge_sql)
            newRechargeRes=yield from new_recharge_ret.fetchall()
            operation_data.newRecharge=len(newRechargeRes)
            #新增充值人数充值额度
            new_recharge_coin_ret=yield from conn.execute(new_recharge_coin_sql)
            newRechargeCoinRes=yield from new_recharge_coin_ret.fetchone()
            operation_data.newRechargeCoin=0 if newRechargeCoinRes[0] is None else int(newRechargeCoinRes[0])/100
            #今日派奖
            pin_award=0 if pin_water_award[1] is None else pin_water_award[1]
            pro_award=0 if pro_water_award[1] is None else int(pro_water_award[1])/100
            operation_data.todayAward=round(pin_award+pro_award,2)
            #提款
            withdrawal=yield from conn.execute(withdrawal_sql)
            withdrawal_count=yield from withdrawal.fetchone()
            operation_data.withdrawal=0 if withdrawal_count[0] is None else int(withdrawal_count[0])/100
            #盈亏：总投注-总派奖
            operation_data.winLoss=round(operation_data.todayWater-operation_data.todayAward,2)

            #vip总输赢
            vip_win_loss=yield from conn.execute(vip_win_loss_sql)
            vip_total_win=yield from vip_win_loss.fetchone()
            vip_bet_total=0 if vip_total_win[0] is None else int(vip_total_win[0])/100
            vip_win_total=0 if vip_total_win[1] is None else int(vip_total_win[1])/100
            agent_data.vipWinLoss=vip_bet_total-vip_win_total
            #代理提款
            agent_withdrawal=yield from conn.execute(agent_withdrawal_sql)
            agentWithdrawal=yield from agent_withdrawal.fetchone()
            agent_data.withdrawal=0 if agentWithdrawal[0] is None else int(agentWithdrawal[0])/100
            #代理总输赢:总投注-总派奖
            agent_total_win=yield from conn.execute(agent_bet_award_sql)
            ag_total_win=yield from agent_total_win.fetchone()
            ag_bet_total=0 if ag_total_win[0] is None else int(ag_total_win[0])/100
            ag_award_total=0 if ag_total_win[1] is None else int(ag_total_win[1])/100
            agent_data.winLoss=ag_bet_total-ag_award_total
            #今日新增线下
            today_new_offline=yield from conn.execute(today_new_offline_sql)
            new_offline=yield from today_new_offline.fetchone()
            agent_data.vipNew=new_offline[0]

        with(yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as connect:
            #代理数据1.代理总数
            agent_count=yield from connect.execute(agent_count_sql)
            total_agent=yield from agent_count.fetchone()
            agent_data.agentCount=total_agent[0]
            #新增代理
            new_agent=yield from connect.execute(agent_new_sql)
            new_agents=yield from new_agent.fetchone()
            agent_data.agentNew=new_agents[0]

        objRep.agentData = agent_data
        objRep.operationData = operation_data
        if days==0:
            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "查询实时数据",
                'actionTime': getNow(),
                'actionMethod': methodName,
                'actionDetail': "查询实时数据",
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)
