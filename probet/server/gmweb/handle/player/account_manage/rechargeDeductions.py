import ast
import asyncio
import json

from appweb.logic.pinboDeposit import deposit
from lib.jsonhelp import classJsonDump
from datawrapper.pushDataOpWrapper import  coroPushPlayerCenterCoin
from gmweb.utils.models import *
import logging
import uuid
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required, permission_required
from logic.data.userData import classUserCoinHistory, classPayData
from logic.logicmgr import checkParamValid as cpv
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.timehelp import timeHelp


class cData():
    def __init__(self):
        self.phone = ""

class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('充值补发/扣款')
@asyncio.coroutine
def handleHttp(request:dict):
    userId=request.get('userId','')
    kind=request.get('kind','')
    money=request.get('money',0)
    reason=request.get('reason','')
    wallet=request.get('wallet','')

    if not all([userId,money,kind,reason]):
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

    if kind not in ['recharge','deductions']:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(userId)
        if objPlayerData is None:
            raise exceptionLogic(errorLogic.player_data_not_found)

        objUserCoinHis=classUserCoinHistory()
        objUserCoinHis.strOrderId=str(uuid.uuid1())
        objUserCoinHis.iTime= timeHelp.getNow()
        objUserCoinHis.iCoin=iCoin
        objUserCoinHis.iTradeState=1
        objUserCoinHis.strAccountId=userId
        objUserCoinHis.strIp=request.get('srcIp','')
        objUserCoinHis.iEndTime= timeHelp.getNow()
        objUserCoinHis.strTransFrom='后台'
        objUserCoinHis.strTransTo='中心钱包'
        objUserCoinHis.strReviewer=request.get('accountId','')
        objUserCoinHis.strReason=reason
        if kind == 'recharge':
            objUserCoinHis.iTradeType=11
            objPlayerData.iCoin += iCoin
            objNewPayOrder = classPayData()
            objNewPayOrder.strPayOrder = objUserCoinHis.strOrderId
            objNewPayOrder.strAccountId = userId
            objNewPayOrder.iBuyCoin = iCoin
            objNewPayOrder.iOrderTime = timeHelp.getNow()
            objNewPayOrder.strIp = request.get("srcIp","")  # str(dictParam.get("srcIp", ""))
            objNewPayOrder.strPayChannel = '后台'
            yield from classDataBaseMgr.getInstance().setPayOrderByLock(objNewPayOrder, save=False,
                                                                        new=True)
            walletName='center'
            coin=objPlayerData.iCoin
        else:
            if wallet not in ['center','pingboCoin','betCoin','shabaCoin']:
                logging.debug(errorLogic.client_param_invalid)
                raise exceptionLogic(errorLogic.client_param_invalid)
            objUserCoinHis.iTradeType = 6
            objUserCoinHis.strTransTo = '后台'
            if wallet=="center":
                objPlayerData.iCoin -= iCoin
                objUserCoinHis.strTransFrom = '中心钱包'
                coin=objPlayerData.iCoin
            elif wallet=="pingboCoin":
                status = yield from deposit(kind='withdraw', accountId=userId, amount=fMoney)
                if status!=1:
                    yield from classDataBaseMgr.getInstance().releasePlayerDataLock(userId,objLock)
                    logging.debug(errorLogic.third_deductions_failed)
                    raise exceptionLogic(errorLogic.third_deductions_failed)
                coin=objPlayerData.iPingboCoin
                if objPlayerData.iPingboCoin-iCoin<0:
                    logging.debug(errorLogic.third_deductions_failed)
                    raise exceptionLogic(errorLogic.third_deductions_failed)
                objPlayerData.iPingboCoin -= iCoin
                objUserCoinHis.strTransFrom = '平博钱包'
            elif wallet=="betCoin":
                coin=objPlayerData.iGuessCoin
                objPlayerData.iGuessCoin -= iCoin
                objUserCoinHis.strTransFrom = '竞猜钱包'
            else:
                coin=objPlayerData.iShabaCoin
                objPlayerData.iShabaCoin -= iCoin
                #todo 调用沙巴扣钱api
                objUserCoinHis.strTransFrom = '沙巴钱包'
            walletName=wallet

        yield from classDataBaseMgr.getInstance().addPlayerCoinRecord(userId,objUserCoinHis)
        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)

        # 推送用户金币
        yield from coroPushPlayerCenterCoin(objPlayerData.strAccountId, coin,walletName)
        yield from asyncio.sleep(1)
        sql="select * from dj_account WHERE accountId='{}' ".format(userId)
        conn=classSqlBaseMgr.getInstance()
        listRest=yield from conn._exeCute(sql)
        user=yield from listRest.fetchone()
        objRsp=cResp()
        data=cData()
        data.accountId = user['accountId']
        data.phone = user['phone']
        data.coin = "%.2f" % round(user['coin'] / 100, 2)
        data.guessCoin = "%.2f" % round(user['guessCoin'] / 100, 2)
        data.pinboCoin = "%.2f" % round(user['pingboCoin'] / 100, 2)
        #todo
        data.coin188 = "%.2f" % round(123123 / 100, 2)
        data.regTime = user['regTime']
        data.email = user['email']
        data.loginTime = user['loginTime']
        data.loginIp = [user['loginIp'], user['loginAddress']]
        data.logoutTime = user['logoutTime']
        data.level = user['level']
        data.status = [user['status'], user['lockEndTime'], user['lockReason']]
        data.bankcard = ast.literal_eval(user['bankcard'])
        data.loginDeviceUdid = user['loginDeviceUdid']
        data.realName=user['realName']
        objRsp.data.append(data)
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "给用户充值/补发" if kind=='recharge' else "给用户扣款",
            'actionTime': timeHelp.getNow(),
            'actionMethod': methodName,
            'actionDetail': "给用户:{},充值/补发:{}，单号:{}".format(userId,money,objUserCoinHis.strOrderId) if kind=='recharge' else "给用户：{}，扣款{},单号:{}".format(userId,money,objUserCoinHis.strOrderId),
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(objRsp)
    except Exception as e:
        logging.exception(e)
        raise e
