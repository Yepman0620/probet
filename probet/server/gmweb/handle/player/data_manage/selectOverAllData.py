import asyncio
import json
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.getPingboValidWater import getPingboValidWaterByParams
from gmweb.utils.tools import token_required, permission_required
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow
from logic.logicmgr.checkParamValid import checkIsInt

class cData():
    def __init__(self):
        self.time=0
        self.totalReg=0
        self.newAccount=0
        self.loginCount=0
        self.recharge=0             #存款
        self.deduction=0            #提款
        self.betAvail=0             #投注收入
        self.awardNum=0             #派奖金额
        self.ACU=0                  #平均在线
        self.PCU=0                  #巅峰在线
        self.rechargeCount=0        #存款人数
        self.firstRechargeCount=0   #首存人数
        self.newRechargeCount=0     #新增存款人数
        self.payPenetration=0       #付费渗透
        self.payConversion=0        #付费转换
        self.totalWater=0           #总流水
        self.validWater=0           #有效流水
        self.pumpingWater=0         #抽水
        self.profitLoss=0           #盈亏
        self.profitLossRatio=0      #盈亏比


class cResp():
    def __init__(self):
        self.ret = 0
        self.count = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('综合数据查询')
@asyncio.coroutine
def handleHttp(request: dict):
    """根据时间，渠道获取综合数据"""
    channel = request.get('channel', '')
    startTime = request.get('startTime', 0)
    endTime = request.get('endTime', 0)
    pn = request.get('pn', 1)
    objRep = cResp()

    if not all([startTime,endTime]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    if (not checkIsInt(startTime)) or (not checkIsInt(endTime)) or (not checkIsInt(pn)):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        conn=classSqlBaseMgr.getInstance(instanceName='probet_oss')
        endTime=endTime+24*3600
        days=(endTime-startTime)/(24*3600)
        days=int(days)
        # 获取综合数据查询
        for x in range((pn-1)*MSG_PAGE_COUNT,pn*MSG_PAGE_COUNT):
            if x>=days:
                break
            data=cData()
            #1.获取截止当前这天的总注册、新增用户、 登录人数、存款、取款、投注收入、
            if channel:
                sql = "select count(DISTINCT(accountId)) from dj_regbill WHERE dj_regbill.agentId='{}' AND dj_regbill.regTime <={} ".format(channel,
                                                                            startTime + x * 24 * 3600)
            else:
                sql="select count(DISTINCT(accountId)) from dj_regbill WHERE dj_regbill.regTime <={} ".format(startTime+x*24*3600)

            listRest=yield from conn._exeCute(sql)
            idList=yield from listRest.fetchone()
            # 总注册量
            reg_count = idList[0]
            data.totalReg = reg_count
            #时间
            data.time = startTime + x * 24 * 3600
            #新增用户：当天
            if channel:
                sql="select count(id) from dj_regbill WHERE dj_regbill.regTime BETWEEN {} AND {} AND dj_regbill.agentId='{}' ".format(startTime+x*24*3600,startTime+(x+1)*24*3600,channel)
            else:
                sql = "select count(id) from dj_regbill WHERE dj_regbill.regTime BETWEEN {} AND {} ".format(
                    startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600)
            listRest=yield from conn._exeCute(sql)
            newAccount=yield from listRest.fetchone()
            data.newAccount=newAccount[0]
            #登录人数：当天
            if channel:
                sql="select count(DISTINCT(accountId)) from dj_loginbill WHERE dj_loginbill.loginTime BETWEEN {} AND {} AND dj_loginbill.agentId='{}'".format(startTime+x*24*3600,
                                                                                                                                     startTime+(x+1)*24*3600,channel)
            else:
                sql = "select count(DISTINCT(accountId)) from dj_loginbill WHERE dj_loginbill.loginTime BETWEEN {} AND {} ".format(
                    startTime + x * 24 * 3600,startTime + (x + 1) * 24 * 3600)
            listRest=yield from conn._exeCute(sql)
            login_count=yield from listRest.fetchone()
            data.loginCount=login_count[0]
            #存款：当天
            if channel:
                sql="select sum(payCoin) from dj_paybill WHERE dj_paybill.payTime BETWEEN {} AND {} AND dj_paybill.agentId='{}' ".format(
                    startTime+x*24*3600,startTime+(x+1)*24*3600,channel)
            else:
                sql = "select sum(payCoin) from dj_paybill WHERE dj_paybill.payTime BETWEEN {} AND {} ".format(
                    startTime + x * 24 * 3600, startTime+(x+1)*24*3600)

            listRest=yield from conn._exeCute(sql)
            totalRecharge=yield from listRest.fetchone()
            data.recharge=0 if totalRecharge[0] is None else int(totalRecharge[0])/100
            #提款:当天
            if channel:
                sql="select sum(withdrawalCoin) from dj_withdrawalbill WHERE dj_withdrawalbill.withdrawalTime BETWEEN {} AND {} AND dj_withdrawalbill.accountId='{}'".format(
                    startTime+x*24*3600,startTime+(x+1)*24*3600,channel)
            else:
                sql = "select sum(withdrawalCoin) from dj_withdrawalbill WHERE dj_withdrawalbill.withdrawalTime BETWEEN {} AND {} ".format(
                    startTime + x * 24 * 3600, startTime+(x+1)*24*3600)
            listRest=yield from conn._exeCute(sql)
            deduction=yield from listRest.fetchone()
            data.deduction=0 if deduction[0] is None else int(deduction[0])/100
            # 投注收入：总投注的金钱
            if channel:
                sql="select sum(betCoinNum),sum(winCoin) from dj_betresultbill WHERE dj_betresultbill.resultTime BETWEEN {} AND {} AND dj_betresultbill.agentId='{}' ".format(
                    startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600,channel)
            else:
                sql = "select sum(betCoinNum),sum(winCoin) from dj_betresultbill WHERE dj_betresultbill.resultTime BETWEEN {} AND {} ".format(
                    startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600)
            pingbo_bet_sql="select sum(toRisk),sum(CASE WHEN winLoss>0 THEN winLoss ELSE 0 END) from dj_pingbobetbill WHERE wagerDateFm BETWEEN {} AND {} AND status='SETTLED' ".format(startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600)
            listRest=yield from conn._exeCute(sql)
            ret=yield from listRest.fetchone()
            result=yield from conn._exeCute(pingbo_bet_sql)
            res=yield from result.fetchone()
            probetAvail=0 if ret[0] is None else int(ret[0])/100
            proAwardNum=0 if ret[1] is None else int(ret[1])/100
            pinBetAvail=0 if res[0] is None else res[0]
            pinAwardNum=0 if res[1] is None else res[1]
            data.betAvail=round((probetAvail+pinBetAvail),2)
            data.awardNum=round((proAwardNum+pinAwardNum),2)

            #todo ACU----APU
            data.ACU=0
            data.PCU=0
            # 存款人数
            if channel:
                sql="select count(DISTINCT(accountId)) from dj_paybill WHERE dj_paybill.payTime BETWEEN {} AND {} AND dj_paybill.agentId='{}' ".format(
                    startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600, channel)
            else:
                sql = "select count(DISTINCT(accountId)) from dj_paybill WHERE dj_paybill.payTime BETWEEN {} AND {} ".format(
                    startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600)
            listRest=yield from conn._exeCute(sql)
            rechargeCount=yield from listRest.fetchone()
            data.rechargeCount=rechargeCount[0]
            # 首存人数：非当天注册
            if channel:
                sql="select count(DISTINCT(accountId)) from dj_paybill WHERE dj_paybill.firstPayTime BETWEEN {} AND {} AND dj_paybill.agentId='{}' ".format(
                    startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600,channel)
            else:
                sql = "select count(DISTINCT(accountId)) from dj_paybill WHERE dj_paybill.firstPayTime BETWEEN {} AND {} ".format(
                    startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600)
            listRest=yield from conn._exeCute(sql)
            firstRechargeCount=yield from listRest.fetchone()
            data.firstRechargeCount=firstRechargeCount[0]
            #新增存款人数：今日注册参与存款的用户
            if channel:
                sql_reg="select accountId from dj_regbill WHERE dj_regbill.regTime BETWEEN {} AND {} AND dj_regbill.agentId='{}' ".format(
                    startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600, channel)
            else:
                sql_reg = "select accountId from dj_regbill WHERE dj_regbill.regTime BETWEEN {} AND {} ".format(
                    startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600)
            listRest=yield from conn._exeCute(sql_reg)
            idList=yield from listRest.fetchall()
            if len(idList)==0:
                data.newRechargeCount=0
            else:
                sql="select count(DISTINCT(accountId)) from dj_paybill WHERE dj_paybill.payTime BETWEEN {} AND {} ".format(
                    startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600)
                sql=sql+" AND dj_paybill.accountId in ("+sql_reg+")"
                listRest=yield from conn._exeCute(sql)
                newRechargeCount=yield from listRest.fetchone()
                data.newRechargeCount=newRechargeCount[0]

            #付费渗透：存款人数/登录人数
            data.payPenetration="%.2f"%round(0,2) if data.loginCount==0 else "%.2f"%round(data.rechargeCount/data.loginCount,2)
            #付费转换：新增付费人数/新增用户
            data.payConversion="%.2f"%round(0,2) if data.newAccount==0 else "%.2f"%round(data.newRechargeCount/data.newAccount,2)
            #总流水
            data.totalWater=data.betAvail
            #有效流水：赔率在1.5倍以上的投注单 todo 亚赔，欧赔，平博和自己平台不一样
            if channel:
                sql="select sum(betCoinNum) from dj_betresultbill WHERE dj_betresultbill.rate>=1.5 AND dj_betresultbill.resultTime BETWEEN {} AND {} AND dj_betresultbill.agentId='{}' ".format(
                    startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600,channel)
            else:
                sql = "select sum(betCoinNum) from dj_betresultbill WHERE dj_betresultbill.rate>=1.5 AND dj_betresultbill.resultTime BETWEEN {} AND {} ".format(
                    startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600)
            listRest=yield from conn._exeCute(sql)
            validWater=yield from listRest.fetchone()
            #pingbo有效流水
            if channel:
                pinValidWater=yield from getPingboValidWaterByParams(loginIds=None,startTime=(startTime + x * 24 * 3600),endTime=(startTime + (x + 1) * 24 * 3600),agentId=channel)
            else:
                pinValidWater = yield from getPingboValidWaterByParams(loginIds=None,
                                                                       startTime=(startTime + x * 24 * 3600),
                                                                       endTime=(startTime + (x + 1) * 24 * 3600))

            proValidWater=0 if validWater[0] is None else int(validWater[0])/100

            data.validWater=round(proValidWater+pinValidWater,2)
            #抽水：投注*抽水比  todo
            data.pumpingWater=round(data.betAvail*0.15,2)
            #盈亏：投注收入-派奖
            data.profitLoss=round(data.betAvail-data.awardNum,2)
            #盈亏比：盈亏/投注收入
            data.profitLossRatio="%.2f"%round(0,2) if data.betAvail==0 else "%.2f"%round(data.profitLoss/data.betAvail,2)

            objRep.data.append(data)
        objRep.count=days
        if pn==1:
            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "综合数据查询",
                'actionTime': getNow(),
                'actionMethod': methodName,
                'actionDetail': "综合数据查询",
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)
