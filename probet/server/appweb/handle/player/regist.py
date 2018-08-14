import json
import uuid
import asyncio

import logging
from config import activeConfig
from lib.jsonhelp import classJsonDump
from lib.timehelp import timeHelp
from logic.data.userData import classUserData, classMessageData
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from appweb.proc import procVariable
from logic.regex import precompile
from lib.ganerateToken import generate_token
from lib.pwdencrypt import PwdEncrypt
from appweb.logic.pinboRegister import register_pinbo
from appweb.logic.active import initActiveData, joinOncePayRebateActive, joinVipPayRebateActive
import hashlib
import random


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
        # self.pinbo_id = ""


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


def welcomeMsg(strAccountId):
    SysMsgData = classMessageData()
    SysMsgData.iMsgTime = timeHelp.getNow()
    SysMsgData.strMsgId = str(uuid.uuid1())
    SysMsgData.strAccountId = strAccountId
    SysMsgData.strMsgTitle = "欢迎加入probet!"
    SysMsgData.strMsgDetail = "尊敬的{}，恭喜您已经成为Probet正式会员。我们将为您提供海量的电竞，体育赛事，同时我们提供便捷的存提款方式让您毫无后顾之忧，" \
                              "probet是注册于菲律宾的合法博彩公司，我们会倾尽全力为您的资金保驾护航，再次欢迎您光临。".format(strAccountId)
    SysMsgData.strSendFrom = "Pro电竞"
    return SysMsgData


@asyncio.coroutine
def handleHttp(dict_param: dict):
    """注册"""

    #TODO 去掉限制注册的提示
    #if not procVariable.debug:
    #    raise exceptionLogic(errorLogic.player_reg_limited)

    objRsp = cResp()

    strAccountId = dict_param.get("accountId", "")
    strPassword = dict_param.get("password", "")
    iCid = dict_param.get("cid", 0)
    source = dict_param.get('source', '')
    if iCid:
        try:
            iCid = int(iCid)
            agentId = yield from classDataBaseMgr.getInstance().getAgentCodeMapping(iCid)
        except Exception as e:
            logging.error(repr(e))
            raise exceptionLogic(errorLogic.client_param_invalid)
    else:
        agentId = ""
    if not all([strAccountId, strPassword, source]):
        raise exceptionLogic(errorLogic.client_param_invalid)

    if precompile.ChineseOrEmptyCharRegex.search(strAccountId):
        raise exceptionLogic(errorLogic.player_pwd_length_out_of_range)

    if precompile.Password.search(strPassword) is None:
        raise exceptionLogic(errorLogic.player_pwd_length_out_of_range)

    objPlayerData  = yield from classDataBaseMgr.getInstance().getPlayerData(strAccountId)
    if objPlayerData is None:
        #注册pinbo
        objPlayerData = classUserData()
        objPlayerData.strAccountId = strAccountId
        objPlayerData.strNick = strAccountId
        objPlayerData.iRegTime = timeHelp.getNow()
        objPlayerData.iLastLoginTime = timeHelp.getNow()
        objPlayerData.strAgentId = agentId
        #objPlayerData.iRandomSecert = random.randint()
        objPlayerData.strPassword = PwdEncrypt().create_md5(strPassword)
        if source == 'pc':
            objPlayerData.strToken = generate_token(strAccountId)
        elif source == 'app':
            objPlayerData.strAppToken = generate_token(strAccountId)
        objPlayerData.strLastLoginIp = dict_param.get("srcIp","")

        if procVariable.debug:
            objPlayerData.iCoin += 100000
            objPlayerData.iGuessCoin += 50000

        #后注册pinbo
        yield from register_pinbo(strAccountId)

        SysMsgData = welcomeMsg(strAccountId)
        yield from classDataBaseMgr.getInstance().addSystemMsg(SysMsgData)
        yield from asyncio.sleep(0.5)
        unReadNum = yield from classSqlBaseMgr.getInstance().getSysMsgUnReadNum(strAccountId)

        yield from initActiveData(strAccountId)

        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, new=True)
    else:
        raise exceptionLogic(errorLogic.player_id_already_exist)

    # 构造回包
    objRsp.data = cData()
    objRsp.data.accountId = strAccountId
    if source == 'pc':
        objRsp.data.token = objPlayerData.strToken
    elif source == 'app':
        objRsp.data.token = objPlayerData.strAppToken
    objRsp.data.nick = objPlayerData.strNick
    objRsp.data.headAddress = ""
    objRsp.data.coin = "%.2f"%round(objPlayerData.iCoin/100, 2)
    objRsp.data.unReadNum = unReadNum
    objRsp.data.phoneNum = objPlayerData.strPhone
    objRsp.data.tradePwd = 0
    objRsp.data.email = objPlayerData.strEmail
    objRsp.data.bankCard = objPlayerData.arrayBankCard
    # objRsp.data.pinbo_id=pinbo_id
    #初始化所有活动
    yield from initActiveData(strAccountId)
    # 日志
    dictReg = {
        'billType': 'regBill',
        'accountId': objPlayerData.strAccountId,
        'regTime': timeHelp.getNow(),
        'regIp':objPlayerData.strLastLoginIp,
        'channel':objPlayerData.iPlatform,
        'regDevice':objPlayerData.strLastDeviceName,
        'agentId':objPlayerData.strAgentId
    }
    logging.getLogger('bill').info(json.dumps(dictReg))

    # 日志
    dictLogin = {
        'billType': 'loginBill',
        'accountId': objPlayerData.strAccountId,
        'agentId': objPlayerData.strAgentId,
        'loginTime': timeHelp.getNow(),
        'coin': objPlayerData.iCoin,
        'vipLevel': objPlayerData.iLevel,
        'loginDevice': objPlayerData.strLastDeviceModal,
        'loginIp': objPlayerData.strLastLoginIp,
        'vipExp': objPlayerData.iLevelValidWater,
    }
    logging.getLogger('bill').info(json.dumps(dictLogin))

    return classJsonDump.dumps(objRsp)
