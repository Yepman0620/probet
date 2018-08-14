
import asyncio
import json

from lib.jsonhelp import classJsonDump
from datawrapper.pushDataOpWrapper import coroPushPlayerCenterCoin
import logging
import uuid
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required, permission_required
from logic.data.userData import classUserCoinHistory
from logic.logicmgr import checkParamValid as cpv
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.timehelp import timeHelp


class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('代理佣金审核')
@asyncio.coroutine
def handleHttp(request:dict):
    """获取佣金报表"""
    objRep = cResp()

    agentId=request.get('agentId','')
    month = request.get('month', 0)
    year = request.get('year', 0)

    if not all([year,month]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        if agentId:
            sql = "select * from dj_agent_commission where agentId=%s and dateYear=%s and dateMonth=%s and (status=1 or status=2)"
            params=[agentId,year,month]
        else:
            sql = "select * from dj_agent_commission where dateYear=%s and dateMonth=%s and (status=1 or status=2) limit 0,10"
            params=[year,month]
        with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
            result = yield from conn.execute(sql,params)
            if result.rowcount<=0:
                return classJsonDump.dumps(objRep)
            else:
                for var in result:
                    commissionData = {}
                    commissionData['billId'] = var.billId
                    commissionData['date'] = str(var.dateYear)+'-'+str(var.dateMonth)
                    commissionData['agentId'] = var.agentId
                    commissionData['winLoss'] = '%.2f'%round(var.winLoss/100,2)
                    commissionData['platformCost'] = '%.2f'%round(var.platformCost/100,2)
                    commissionData['backWater'] = '%.2f'%round(var.backWater/100,2)
                    commissionData['bonus'] = '%.2f'%round(var.bonus/100,2)
                    commissionData['poundage'] = '%.2f'%round(var.depositDrawingCost/100,2)
                    commissionData['balance'] = '%.2f'%round(var.preBalance/100,2)
                    commissionData['commissionRate'] = var.commissionRate
                    commissionData['commission'] = '%.2f'%round(var.commission/100,2)
                    objRep.data.append(commissionData)
            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "查询佣金报表",
                'actionTime': timeHelp.getNow(),
                'actionMethod': methodName,
                'actionDetail': "查询代理：{}，佣金报表".format(agentId),
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))
            return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)
        raise e

