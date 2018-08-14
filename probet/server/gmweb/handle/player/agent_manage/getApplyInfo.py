import json
import asyncio
import logging
from lib.jsonhelp import classJsonDump
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.tools import token_required, permission_required


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('代理审核')
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """代理申请查询"""
    objRsp = cResp()

    startTime = dict_param.get("startTime", 0)
    endTime = dict_param.get("endTime", 0)

    if not all([startTime,endTime]):
        sql = "select * from dj_agent_apply"
        params = []
    else:
        sql = "select * from dj_agent_apply where applyTime between %s and %s"
        params = [startTime,endTime]
    try:
        with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
            result = yield from conn.execute(sql,params)
            if result.rowcount <= 0:
                return classJsonDump.dumps(objRsp)
            else:
                for var_row in result:
                    applyInfo = {}
                    applyInfo['agentId'] = var_row.agentId
                    applyInfo['time'] = var_row.applyTime
                    applyInfo['qq'] = var_row.qq
                    applyInfo['website'] = var_row.website
                    applyInfo['introduction'] = var_row.introduction
                    applyInfo['status'] = var_row.status
                    objRsp.data.append(applyInfo)
                return classJsonDump.dumps(objRsp)
    except Exception as e:
        logging.error(repr(e))
        raise e

