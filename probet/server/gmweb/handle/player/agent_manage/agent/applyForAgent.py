import json
import asyncio
import logging
from lib.jsonhelp import classJsonDump
from lib.timehelp import timeHelp
from logic.data.userData import classApplyForAgent
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.dataBaseMgr import classDataBaseMgr


class cData():
    def __init__(self):
        self.agentId = ""

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@asyncio.coroutine
def handleHttp(dict_param: dict):
    """代理申请"""
    objRsp = cResp()

    agentId = dict_param.get("agentId", "")
    qq = dict_param.get("qq", "")
    website = dict_param.get("website", "")
    introduction = dict_param.get("introduction", "")

    if not all([agentId,qq,introduction]):
        raise exceptionLogic(errorLogic.client_param_invalid)
    objPlayerData= yield from classDataBaseMgr.getInstance().getPlayerData(agentId)
    if objPlayerData is None:
        raise exceptionLogic(errorLogic.user_data_not_found)
    applyInfo = classApplyForAgent()
    applyInfo.strAgentId = agentId
    applyInfo.strQQ = qq
    applyInfo.strWebsite = website
    applyInfo.strDesc = introduction
    try:
        from gmweb.utils.models import Base
        tbl = Base.metadata.tables["dj_agent_apply"]
        sql = tbl.insert().values(
            agentId=agentId,
            applyTime=timeHelp.getNow(),
            qq=qq,
            website=website,
            introduction=introduction,
            status=1,
        )
        with (yield from classSqlBaseMgr.getInstance().getEngine()) as conn:
            yield from conn.execute(sql)
    except Exception as e:
        logging.error(repr(e))
        raise exceptionLogic(errorLogic.db_error)

    # yield from classDataBaseMgr.getInstance().setApplyInfo(applyInfo)

    # 构造回包
    objRsp.data = cData()
    objRsp.data.agentId = agentId
    return classJsonDump.dumps(objRsp)
