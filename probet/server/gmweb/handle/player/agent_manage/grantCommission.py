
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
    """佣金发放"""

    agentId=request.get('agentId','')
    billId=request.get('billId','')
    money=request.get('commission',0)

    if not all([agentId,billId,money]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    if cpv.checkIsString(money):
        raise exceptionLogic(errorLogic.client_param_invalid)
    fMoney = float(money)
    if not cpv.checkIsFloat(fMoney):
        raise exceptionLogic(errorLogic.client_param_invalid)
    iCoin = int(fMoney * 100)
    if not cpv.checkIsInt(iCoin):
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(agentId)
        if objPlayerData is None:
            raise exceptionLogic(errorLogic.player_data_not_found)

        objUserCoinHis=classUserCoinHistory()
        objUserCoinHis.strOrderId=str(uuid.uuid1())
        objUserCoinHis.iTime=getNow()
        objUserCoinHis.iCoin=iCoin
        objUserCoinHis.iBalance=objPlayerData.iCoin
        objUserCoinHis.iTradeState=1
        objUserCoinHis.strAccountId=agentId
        objUserCoinHis.strIp=request.get('srcIp','')
        objUserCoinHis.iEndTime=getNow()
        objUserCoinHis.strTransFrom='后台'
        objUserCoinHis.strTransTo='中心钱包'
        objUserCoinHis.strReviewer=request.get('accountId','')
        objUserCoinHis.strReason='佣金发放'
        objUserCoinHis.iTradeType=10

        commissionData = yield from classDataBaseMgr.getInstance().getCommissionData(billId)
        commissionData.iStatus = 0
        yield from classDataBaseMgr.getInstance().addAgentCommissionData(commissionData,billId)
        objPlayerData.iCoin += iCoin
        yield from classDataBaseMgr.getInstance().addPlayerCoinRecord(agentId,objUserCoinHis)
        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)
        # 推送用户金币
        wallet = "center"
        yield from coroPushPlayerCenterCoin(objPlayerData.strAccountId,objPlayerData.iCoin, wallet)
        yield from asyncio.sleep(1)
        sql="select * from dj_account WHERE accountId='{}' ".format(agentId)
        conn=classSqlBaseMgr.getInstance()
        listRest=yield from conn._exeCute(sql)
        user=yield from listRest.fetchone()
        objRsp=cResp()
        data=cData()
        data.accountId = user['accountId']
        data.phone = user['phone']
        data.coin = "%.2f" % round(user['coin'] / 100, 2)
        data.guessCoin = "%.2f" % round(user['guessCoin'] / 100, 2)
        data.pinboCoin = "%.2f" % round(12312 / 100, 2)
        data.coin188 = "%.2f" % round(123123 / 100, 2)
        data.regTime = user['regTime']
        data.email = user['email']
        data.loginTime = user['loginTime']
        data.loginIp = [user['loginIp'], user['loginAddress']]
        data.logoutTime = user['logoutTime']
        data.level = user['level']
        data.status = [user['status'], user['lockEndTime'], user['lockReason']]
        data.bankcard = eval(user['bankcard'])
        data.loginDeviceUdid = user['loginDeviceUdid']
        objRsp.data.append(data)

        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "给代理发放佣金",
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionDetail': "给代理:{}发放佣金:{}，单号:{}".format(agentId,money,objUserCoinHis.strOrderId),
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))

        #TODO 自动发通知消息
        return classJsonDump.dumps(objRsp)
    except Exception as e:
        logging.exception(e)
        raise e

