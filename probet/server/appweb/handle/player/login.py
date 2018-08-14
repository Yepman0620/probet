import asyncio
import json
import logging
from gmweb.handle.pinbo.update_player_status import update_status
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic,errorLogic
from lib.ganerateToken import generate_token
from lib.certifytoken import certify_token
from lib.pwdencrypt import PwdEncrypt
from lib.timehelp import timeHelp


class cData():
    def __init__(self):
        self.token = ""
        self.accountId = ""
        self.nick = ""
        self.headAddress = ""
        self.coin = 0
        self.unReadNum = 0
        self.phoneNum = ""
        self.email = ""
        self.bankCard = []
        self.tradePwd = 0


class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = ""


@asyncio.coroutine
def handleHttp(dict_param: dict):
    """登陆"""
    objRsp = cResp()

    # TODO 多设备同时登陆
    source = dict_param.get('source','pc')
    strAccountId = dict_param.get("accountId", "")
    strPassword = dict_param.get("password", "")
    strToken = dict_param.get("token", "")
    if not all([strAccountId, source]):
        raise exceptionLogic(errorLogic.client_param_invalid)

    if strToken or strPassword:
        if strPassword:
            strPwd = PwdEncrypt().create_md5(strPassword)

            objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)

            if objPlayerData is None:
                raise exceptionLogic(errorLogic.player_data_not_found)
            if strPwd != objPlayerData.strPassword:
                yield from classDataBaseMgr.getInstance().releasePlayerDataLock(strAccountId, objLock)
                raise exceptionLogic(errorLogic.login_pwd_not_valid)
            if timeHelp.getNow() < objPlayerData.iLockEndTime:
                yield from classDataBaseMgr.getInstance().releasePlayerDataLock(strAccountId, objLock)
                raise exceptionLogic(errorLogic.player_id_invalid)
            else:
                if source == 'pc':
                    objPlayerData.strToken = generate_token(strAccountId)
                elif source == 'app':
                    objPlayerData.strAppToken = generate_token(strAccountId)
                else:
                    raise exceptionLogic(errorLogic.client_param_invalid)
                objPlayerData.iStatus = 0
                objPlayerData.iLockStartTime = 0
                objPlayerData.iLockEndTime = 0
                objPlayerData.strLockReason = ""
                objPlayerData.strLastDeviceName = ""#macAddr
                objPlayerData.iLastLoginTime = timeHelp.getNow()
                objPlayerData.strLastLoginIp = dict_param.get("srcIp", "")
                yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)
                #yield from update_status(strAccountId, 'ACTIVE')
            unReadNum = yield from classSqlBaseMgr.getInstance().getSysMsgUnReadNum(strAccountId)
        else:
            certify_token(strAccountId, strToken)
            objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)

            if objPlayerData is None:
                raise exceptionLogic(errorLogic.player_data_not_found)
            if source == 'pc':
                if strToken != objPlayerData.strToken:
                    yield from classDataBaseMgr.getInstance().releasePlayerDataLock(strAccountId, objLock)
                    raise exceptionLogic(errorLogic.login_token_not_valid)
            elif source == 'app':
                if strToken != objPlayerData.strAppToken:
                    yield from classDataBaseMgr.getInstance().releasePlayerDataLock(strAccountId, objLock)
                    raise exceptionLogic(errorLogic.login_token_not_valid)
            else:
                raise exceptionLogic(errorLogic.client_param_invalid)
            if timeHelp.getNow() < objPlayerData.iLockEndTime:
                yield from classDataBaseMgr.getInstance().releasePlayerDataLock(strAccountId, objLock)
                raise exceptionLogic(errorLogic.player_id_invalid)
            else:
                objPlayerData.iStatus = 0
                objPlayerData.iLockStartTime = 0
                objPlayerData.iLockEndTime = 0
                objPlayerData.strLockReason = ""
                objPlayerData.iLastLoginTime = timeHelp.getNow()
                objPlayerData.strLastLoginIp = dict_param.get("srcIp", "")
                objPlayerData.strLastDeviceName = ""#macAddr
                yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)
                # yield from update_status(strAccountId, 'ACTIVE')
            unReadNum = yield from classSqlBaseMgr.getInstance().getSysMsgUnReadNum(strAccountId)
    else:
        raise exceptionLogic(errorLogic.client_param_invalid)

    # 构造回包
    objRsp.data = cData()
    if source == "pc":
        objRsp.data.token = objPlayerData.strToken
    elif source == "app":
        objRsp.data.token = objPlayerData.strAppToken
    objRsp.data.accountId = objPlayerData.strAccountId
    objRsp.data.nick = objPlayerData.strNick
    objRsp.data.coin = "%.2f" % round(objPlayerData.iCoin / 100, 2)
    objRsp.data.headAddress = objPlayerData.strHeadAddress
    objRsp.data.unReadNum = unReadNum
    objRsp.data.phoneNum = objPlayerData.strPhone
    objRsp.data.realName = objPlayerData.strRealName
    objRsp.data.sex = objPlayerData.strSex
    objRsp.data.born = objPlayerData.strBorn
    objRsp.data.address = objPlayerData.dictAddress
    objRsp.data.userType = objPlayerData.iUserType
    objRsp.data.mac = objPlayerData.strLastDeviceName
    if objPlayerData.strTradePassword:
        objRsp.data.tradePwd = 1
    else:
        objRsp.data.tradePwd = 0
    objRsp.data.email = objPlayerData.strEmail
    objRsp.data.bankCard = objPlayerData.arrayBankCard
    #日志
    dictLogin={
        'billType':'loginBill',
        'accountId': objPlayerData.strAccountId,
        'agentId':objPlayerData.strAgentId,
        'loginTime': timeHelp.getNow(),
        'coin':objPlayerData.iCoin,
        'vipLevel':objPlayerData.iLevel,
        'loginDevice':objPlayerData.strLastDeviceModal,
        'loginIp':objPlayerData.strLastLoginIp,
        'vipExp':objPlayerData.iLevelValidWater,
    }
    logging.getLogger('bill').info(json.dumps(dictLogin))

    return classJsonDump.dumps(objRsp)



