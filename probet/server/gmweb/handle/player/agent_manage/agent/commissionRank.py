
import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from datetime import datetime


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@asyncio.coroutine
def handleHttp(request:dict):
    """每月佣金排行榜"""

    objRsp = cResp()
    year = datetime.now().year
    month = datetime.now().month
    with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
        sql = "select agentId,commission from dj_agent_commission where dateYear=%s and dateMonth=%s order by commission desc limit 0,10"
        result = yield from conn.execute(sql,[year,month])
        if result.rowcount <= 0:
            return classJsonDump.dumps(objRsp)
        else:
            for var_row in result:
                objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(var_row.agentId)
                x = {}
                x['agentId'] = var_row.agentId[0:4]+"*****"
                x['head'] = objPlayerData.strHeadAddress
                x['commission'] = '%.2f'%round(var_row.commission/100,2)
                objRsp.data.append(x)

        return classJsonDump.dumps(objRsp)

