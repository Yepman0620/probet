import asyncio
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.tools import token_required
from lib.jsonhelp import classJsonDump

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@asyncio.coroutine
def handleHttp(request: dict):
    """获取获取所有代理账号"""
    objRep = cResp()

    try:
        with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
            sql="select agentId from dj_agent"
            listRet=yield from conn.execute(sql)
            resList=yield from listRet.fetchall()
            for x in resList:
                objRep.data.append(x[0])
            return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)