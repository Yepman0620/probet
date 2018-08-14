import json
import random
import asyncio
import logging
from lib.jsonhelp import classJsonDump
from lib.timehelp import timeHelp
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from datawrapper.dataBaseMgr import classDataBaseMgr
from logic.data.userData import classAgentData


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('代理审核')
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """代理审核"""
    objRsp = cResp()

    agentId = dict_param.get("agentId", "")
    kind = dict_param.get("kind", "")

    if not all([agentId,kind]):
        raise exceptionLogic(errorLogic.client_param_invalid)
    if kind == 'refuse':
        sql = "update dj_agent_apply set status=2 where agentId=%s"
        with (yield from classSqlBaseMgr.getInstance().getEngine()) as conn:
            yield from conn.execute(sql,[agentId])
    elif kind == 'pass':
        objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(agentId)
        if objPlayerData is None:
            raise exceptionLogic(errorLogic.player_data_not_found)
        if objPlayerData.iUserType == 2:
            raise exceptionLogic(errorLogic.agent_id_already_exist)

        while True:
            cid = random.randint(100000,999999)
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
            from gmweb.utils.models import Base
            tbl = Base.metadata.tables["dj_agent"]
            sql = tbl.insert().values(
                agentId=agentId,
                regTime=timeHelp.getNow(),
                code=cid,
            )
            with (yield from classSqlBaseMgr.getInstance().getEngine()) as conn:
                yield from conn.execute(sql)
                sql_update = "update dj_agent_apply set status=0 where agentId=%s"
                yield from conn.execute(sql_update,[agentId])
        except Exception as e:
            logging.error(repr(e))
            raise exceptionLogic(errorLogic.db_error)
    elif kind == 'stop':
        objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(agentId)
        if objPlayerData is None:
            raise exceptionLogic(errorLogic.player_data_not_found)
        objPlayerData.iUserType = 1
        yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)
        sql = "update dj_agent_apply set status=3 where agentId=%s"
        with (yield from classSqlBaseMgr.getInstance().getEngine()) as conn:
            yield from conn.execute(sql, [agentId])

    fileName = __name__
    nameList = fileName.split('.')
    methodName = nameList.pop()
    # 日志
    dictActionBill = {
        'billType': 'adminActionBill',
        'accountId': dict_param.get('accountId', ''),
        'action': "代理审核",
        'actionTime': timeHelp.getNow(),
        'actionMethod': methodName,
        'actionDetail': "代理：{} 审核".format(agentId),
        'actionIp': dict_param.get('srcIp', ''),
    }
    logging.getLogger('bill').info(json.dumps(dictActionBill))
    return classJsonDump.dumps(objRsp)
