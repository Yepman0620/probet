
import asyncio
import json
from lib.timehelp.timeHelp import getNow
from lib.jsonhelp import classJsonDump
from datawrapper.pushDataOpWrapper import coroPushPlayerCenterCoin
from gmweb.utils.models import *
import logging
import uuid
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required, permission_required
from logic.data.userData import classUserCoinHistory
from logic.logicmgr import checkParamValid as cpv
from datawrapper.dataBaseMgr import classDataBaseMgr

class cData():
    def __init__(self):
        self.phone = ""

class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('代理佣金审核')
@asyncio.coroutine
def handleHttp(request:dict):
    """佣金调整"""
    objRep = cResp()

    agentId=request.get('agentId','')
    billId=request.get('billId','')
    winLoss=request.get('winLoss',0)
    platformCost=request.get('platformCost',0)
    backWater=request.get('backWater',0)
    bonus=request.get('bonus',0)
    poundage=request.get('poundage',0)
    commissionRate=request.get('commissionRate',0)
    commission=request.get('commission',0)

    if not all([agentId,billId,winLoss,platformCost,backWater,bonus,poundage,commissionRate,commission]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    winLoss = float(winLoss)*100
    platformCost = float(platformCost)*100
    backWater = float(backWater)*100
    bonus = float(bonus)*100
    poundage = float(poundage)*100
    commission = float(commission)*100
    commissionRate = float(commissionRate)

    try:
        with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
            sql = "update dj_agent_commission set winLoss=%s,platformCost=%s,backWater=%s,bonus=%s,depositDrawingCost=%s,commissionRate=%s,commission=%s where billId=%s"
            params = [winLoss,platformCost,backWater,bonus,poundage,commissionRate,commission,billId]
            yield from conn.execute(sql, params)
            sql_select = "select * from dj_agent_commission where billId=%s"
            result = yield from conn.execute(sql_select,[billId])

            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "调整代理的佣金比例",
                'actionTime': getNow(),
                'actionMethod': methodName,
                'actionDetail': "调整代理：{} 的佣金比例".format(agentId),
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))

            if result.rowcount <= 0:
                return classJsonDump.dumps(objRep)
            else:
                for var in result:
                    commissionData = {}
                    commissionData['billId'] = var.billId
                    commissionData['date'] = str(var.dateYear) + '-' + str(var.dateMonth)
                    commissionData['agentId'] = var.agentId
                    commissionData['winLoss'] = '%.2f' % round(var.winLoss / 100, 2)
                    commissionData['platformCost'] = '%.2f' % round(var.platformCost / 100, 2)
                    commissionData['backWater'] = '%.2f' % round(var.backWater / 100, 2)
                    commissionData['bonus'] = '%.2f' % round(var.bonus / 100, 2)
                    commissionData['poundage'] = '%.2f' % round(var.depositDrawingCost / 100, 2)
                    commissionData['commissionRate'] = var.commissionRate
                    commissionData['commission'] = '%.2f' % round(var.commission / 100, 2)
                    objRep.data.append(commissionData)
                return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)
        raise e

