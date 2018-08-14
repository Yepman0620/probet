import asyncio
import json
import logging
from lib.jsonhelp import classJsonDump
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic,errorLogic
from lib.ganerateToken import generate_token
from lib.certifytoken import certify_token
from lib.pwdencrypt import PwdEncrypt
from lib.timehelp import timeHelp
from logic.data.userData import classAgentData


class cData():
    def __init__(self):
        self.token = ""
        self.agentId = ""
        self.count = 0


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@asyncio.coroutine
def handleHttp(dict_param: dict):
    """app登陆"""
    objRsp = cResp()

    agentId = dict_param.get("agentId", "")
    password = dict_param.get("password", "")
    token = dict_param.get("token", "")
    if not agentId:
        raise exceptionLogic(errorLogic.client_param_invalid)
    if password or token:
        if password:
            strPwd = PwdEncrypt().create_md5(password)

            objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(agentId)
            objAgentData = yield from classDataBaseMgr.getInstance().getAgentData(agentId)
            if objPlayerData is None:
                raise exceptionLogic(errorLogic.player_data_not_found)
            sql = "select status from dj_agent_apply where agentId=%s"
            with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
                result = yield from conn.execute(sql, [agentId])
                if result.rowcount <= 0:
                    raise exceptionLogic(errorLogic.agent_data_not_found)
                else:
                    for var_row in result:
                        status = var_row.status
            if status == 1:
                raise exceptionLogic(errorLogic.agent_id_under_review)
            if objAgentData is None:
                raise exceptionLogic(errorLogic.agent_data_not_found)
            if objPlayerData.iUserType != 2:
                raise exceptionLogic(errorLogic.agent_data_not_found)
            if strPwd != objPlayerData.strPassword:
                yield from classDataBaseMgr.getInstance().releasePlayerDataLock(agentId, objLock)
                raise exceptionLogic(errorLogic.login_pwd_not_valid)
            if timeHelp.getNow() < objPlayerData.iLockEndTime:
                yield from classDataBaseMgr.getInstance().releasePlayerDataLock(agentId, objLock)
                raise exceptionLogic(errorLogic.player_id_invalid)
            else:
                # objAgentData.strAppToken = generate_token(agentId)
                objAgentData.strToken = generate_token(agentId)
                objPlayerData.iStatus = 0
                objPlayerData.iLockStartTime = 0
                objPlayerData.iLockEndTime = 0
                objPlayerData.strLockReason = ""
                objPlayerData.iLastLoginTime = timeHelp.getNow()
                yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)

        else:
            certify_token(agentId, token)
            objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(agentId)
            objAgentData = yield from classDataBaseMgr.getInstance().getAgentData(agentId)
            if objPlayerData is None:
                raise exceptionLogic(errorLogic.user_data_not_found)
            sql = "select status from dj_agent_apply where agentId=%s"
            with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
                result = yield from conn.execute(sql, [agentId])
                if result.rowcount <= 0:
                    raise exceptionLogic(errorLogic.agent_data_not_found)
                else:
                    for var_row in result:
                        status = var_row.status
            if status == 1:
                raise exceptionLogic(errorLogic.agent_id_under_review)
            if objAgentData is None:
                raise exceptionLogic(errorLogic.agent_data_not_found)
            if objPlayerData.iUserType != 2:
                raise exceptionLogic(errorLogic.agent_data_not_found)
            # if token != objAgentData.strAppToken:
            if token != objAgentData.strToken:
                raise exceptionLogic(errorLogic.login_token_not_valid)
            if timeHelp.getNow() < objAgentData.iLockEndTime:
                raise exceptionLogic(errorLogic.player_id_invalid)
            else:
                objAgentData.iStatus = 0
                objAgentData.iLockStartTime = 0
                objAgentData.iLockEndTime = 0
                objAgentData.strLockReason = ""
        yield from classDataBaseMgr.getInstance().setAgentData(objAgentData)
        unReadNum = yield from classSqlBaseMgr.getInstance().getAgentMsgUnReadNum(agentId)
        # 构造回包
        objRsp.data = cData()
        objRsp.data.agentId = objPlayerData.strAccountId
        objRsp.data.token = objAgentData.strToken
        objRsp.data.cid = objAgentData.iCid
        objRsp.data.headAddress = objPlayerData.strHeadAddress
        objRsp.data.count = unReadNum
        return classJsonDump.dumps(objRsp)
    else:
        raise exceptionLogic(errorLogic.client_param_invalid)






