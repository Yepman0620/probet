import json
import asyncio
import logging
import random
from lib.jsonhelp import classJsonDump
from lib.timehelp import timeHelp
from logic.data.userData import classAgentData,classUserData
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from logic.regex import precompile
from lib.ganerateToken import generate_token
from lib.pwdencrypt import PwdEncrypt
from gmweb.utils.tools import token_required, permission_required
from datawrapper.dataBaseMgr import classDataBaseMgr


class cData():
    def __init__(self):
        self.agentId = ""

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""

@token_required
@permission_required('代理注册')
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """代理注册"""
    objRsp = cResp()

    agentId = dict_param.get("agentId", "")

    if not agentId:
        raise exceptionLogic(errorLogic.client_param_invalid)

    if precompile.ChineseOrEmptyCharRegex.search(agentId):
        raise exceptionLogic(errorLogic.player_pwd_length_out_of_range)

    objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(agentId)
    if objPlayerData is None:
        raise exceptionLogic(errorLogic.player_data_not_found)
    if objPlayerData.iUserType == 2:
        raise exceptionLogic(errorLogic.agent_id_already_exist)
    while True:
        cid = random.randint(100000, 999999)
        ret = yield from classDataBaseMgr.getInstance().checkCid(cid)
        if ret == 1:
            continue
        else:
            break
    yield from classDataBaseMgr.getInstance().setCid(cid)

    objPlayerData.iUserType = 2
    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)
    objAgentData = classAgentData()
    objAgentData.strAgentId = agentId
    objAgentData.iRegTime = timeHelp.getNow()
    objAgentData.iCid = cid
    yield from classDataBaseMgr.getInstance().setAgentData(objAgentData)
    yield from classDataBaseMgr.getInstance().setAgentCodeMapping(agentId,cid)
    try:
        sql = "select agentId from dj_agent where agentId='{}' ".format(agentId)
        result = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
        if result.rowcount <= 0:
            from gmweb.utils.models import Base
            tbl = Base.metadata.tables["dj_agent"]
            sql = tbl.insert().values(
                agentId=objAgentData.strAgentId,
                regTime=objAgentData.iRegTime,
                code=cid,
            )
            yield from classSqlBaseMgr.getInstance()._exeCuteCommit(sql)
            tb = Base.metadata.tables["dj_agent_apply"]
            sql = tb.insert().values(
                agentId=objAgentData.strAgentId,
                applyTime=objAgentData.iRegTime,
                status=0,
            )
            yield from classSqlBaseMgr.getInstance()._exeCuteCommit(sql)
        else:
            raise exceptionLogic(errorLogic.player_id_already_exist)


    except Exception as e:
        logging.exception(e)

    # 构造回包
    objRsp.data = cData()
    objRsp.data.agentId = objPlayerData.strAccountId
    fileName = __name__
    nameList = fileName.split('.')
    methodName = nameList.pop()
    # 日志
    dictActionBill = {
        'billType': 'adminActionBill',
        'accountId': dict_param.get('accountId', ''),
        'action': "注册代理",
        'actionTime': timeHelp.getNow(),
        'actionMethod': methodName,
        'actionDetail': "注册代理：{}".format(agentId),
        'actionIp': dict_param.get('srcIp', ''),
    }
    logging.getLogger('bill').info(json.dumps(dictActionBill))
    return classJsonDump.dumps(objRsp)
