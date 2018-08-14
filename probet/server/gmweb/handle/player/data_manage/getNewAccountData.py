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
        self.time = 0
        self.newAccountCount=0          #新增用户
        self.newLoginCount=0            #新增用户登录数
        self.rechargeCount=0            #当天充值人数
        self.payPenetration='0.00'      #付费渗透
        self.newTotalWater=0            #新增用户总流水
        self.newValidWater=0            #新增用户有效流水
        self.newPumpingWater=0          #新增用户抽水
        self.newRecharge=0              #新增用户充值
        self.newWithdrawal=0            #新增用户提款
        self.betAvail=0                 #投注收入
        self.awardNum=0                 #派奖金额
        self.profitLoss = 0             # 盈亏
        self.profitLossRatio ='0.00'    # 盈亏比
        self.LTV='0.00'                 #新增用户存款/新增用户数

class cResp():
    def __init__(self):
        self.ret = 0
        self.count = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('新增用户查询')
@asyncio.coroutine
def handleHttp(request: dict):
    """获取新增用户数据"""
    objRep = cResp()

    channel = request.get('channel', '')
    startTime = request.get('startTime', 0)
    endTime = request.get('endTime', 0)
    pn = request.get('pn', 1)
    if not all([startTime, endTime]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    if (not checkIsInt(startTime)) or (not checkIsInt(endTime)) or (not checkIsInt(pn)):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        conn = classSqlBaseMgr.getInstance(instanceName='probet_oss')
        endTime=endTime+24*3600
        days = (endTime - startTime) / (24 * 3600)
        days = int(days)
        for x in range((pn-1)*MSG_PAGE_COUNT,pn*MSG_PAGE_COUNT):
            if x>=days:
                break
            data = cData()
            #时间
            data.time = startTime + x * 24 * 3600
            if channel:
                new_sql="select accountId from dj_regbill WHERE dj_regbill.regTime BETWEEN {} AND {} AND dj_regbill.agentId='{}' ".format(startTime+x*24*3600,startTime+(x+1)*24*3600,channel)
            else:
                new_sql = "select accountId from dj_regbill WHERE dj_regbill.regTime BETWEEN {} AND {} ".format(
                    startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600)
            listRest=yield from conn._exeCute(new_sql)
            idList=yield from listRest.fetchall()
            #新增用户
            data.newAccountCount=len(idList)
            pinboNewIds=['probet.'+accountId[0] for accountId in idList]
            #新增登陆数
            sql="select count(DISTINCT(accountId)) from dj_loginbill WHERE dj_loginbill.accountId in ("+new_sql+") AND dj_loginbill.loginTime BETWEEN {} AND {} " .format(
                startTime+x*24*3600,startTime+(x+1)*24*3600)
            listRest=yield from conn._exeCute(sql)
            newLoginCount=yield from listRest.fetchone()
            data.newLoginCount=newLoginCount[0]
            #新增用户充值人数
            sql="select count(DISTINCT(accountId)) from dj_paybill WHERE dj_paybill.accountId in ("+new_sql+") AND dj_paybill.payTime BETWEEN {} AND {} ".format(
                startTime+x*24*3600,startTime+(x+1)*24*3600)
            listRest = yield from conn._exeCute(sql)
            rechargeCount = yield from listRest.fetchone()
            data.rechargeCount = rechargeCount[0]
            #付费渗透
            data.payPenetration="%.2f"%round(0,2) if data.newLoginCount==0 else "%.2f"%round(data.rechargeCount/data.newLoginCount,2)
            #新增用户总流水,派奖金额
            sql="select sum(betCoinNum),sum(winCoin) from dj_betresultbill WHERE dj_betresultbill.accountId in ("+new_sql+") AND dj_betresultbill.resultTime BETWEEN {} AND {} ".format(
                startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600)
            if len(pinboNewIds)==0:
                pin_water=0
                pin_award=0
                pin_valid_water=0
            else:
                if len(pinboNewIds)==1:
                    pinNewIds=str(tuple(pinboNewIds)).replace(r',','',1)
                else:
                    pinNewIds=tuple(pinboNewIds)
                pin_water_sql="select sum(toRisk),sum(CASE WHEN winLoss>0 THEN winLoss ELSE 0 END) from dj_pingbobetbill WHERE loginId in {} AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} ".format(pinNewIds,startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600)
                pinRet=yield from conn._exeCute(pin_water_sql)
                pin_water_win=yield from pinRet.fetchone()
                pin_water=0 if pin_water_win[0] is None else pin_water_win[0]
                pin_award=0 if pin_water_win[1] is None else pin_water_win[1]
                pin_valid_water=yield from getPingboValidWaterByParams(loginIds=pinboNewIds,startTime=(startTime + x * 24 * 3600),endTime=(startTime + (x + 1) * 24 * 3600))

            listRest=yield from conn._exeCute(sql)
            totalWater=yield from listRest.fetchone()
            pro_water=round(0,2) if totalWater[0] is None else round(int(totalWater[0])/100,2)
            pro_award=round(0, 2) if totalWater[1] is None else round(int(totalWater[1]) / 100, 2)
            data.awardNum = pro_award+pin_award
            data.newTotalWater=pro_water+pin_water
            #新增用户有效流水：赔率在1.5倍以上的投注单 todo 亚赔，欧赔，平博和自己平台不一样
            sql = "select sum(betCoinNum) from dj_betresultbill WHERE dj_betresultbill.rate>=1.5 AND dj_betresultbill.accountId IN ("+new_sql+") AND dj_betresultbill.resultTime BETWEEN {} AND {} ".format(
                startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600)
            listRest=yield from conn._exeCute(sql)
            validWater=yield from listRest.fetchone()
            pro_valid_water=round(0,2) if validWater[0] is None else round(int(validWater[0])/100,2)
            data.newValidWater=pin_valid_water+pro_valid_water
            #新增用户抽水   todo
            data.newPumpingWater="%.2f"%round(data.newTotalWater*0.15,2)
            #新增用户存款
            sql="select sum(payCoin) from dj_paybill WHERE dj_paybill.accountId in ("+new_sql+") AND dj_paybill.payTime BETWEEN {} AND {} ".format(
                startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600)
            listRest = yield from conn._exeCute(sql)
            newRecharge = yield from listRest.fetchone()
            data.newRecharge = round(0,2) if newRecharge[0] is None else round(int(newRecharge[0]) / 100,2)
            #新增用户提款
            sql="select sum(withdrawalCoin) from dj_withdrawalbill WHERE dj_withdrawalbill.accountId in ("+new_sql+") AND dj_withdrawalbill.withdrawalTime BETWEEN {} AND {} ".format(
                startTime + x * 24 * 3600, startTime + (x + 1) * 24 * 3600)
            listRest = yield from conn._exeCute(sql)
            newWithdrawal = yield from listRest.fetchone()
            data.newWithdrawal = 0 if newWithdrawal[0] is None else int(newWithdrawal[0]) / 100
            #投注收入=总流水
            data.betAvail = data.newTotalWater

            #盈亏
            data.profitLoss=data.betAvail-data.awardNum
            #盈亏比
            # 盈亏比：盈亏/投注收入
            data.profitLossRatio = "%.2f" % round(0, 2) if data.betAvail == 0 else "%.2f" % round(
                data.profitLoss / data.betAvail, 2)
            #LTV:新增用户存款/新增用户数
            data.LTV="%.2f"%round(0,2) if data.newAccountCount==0 else "%.2f"%round(data.newRecharge/data.newAccountCount,2)
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
                'action': "查询新增账户数据",
                'actionTime': getNow(),
                'actionMethod': methodName,
                'actionDetail': "查询新增账户数据",
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)