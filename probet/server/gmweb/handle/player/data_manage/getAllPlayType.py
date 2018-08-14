import asyncio
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.tools import token_required
from lib.jsonhelp import classJsonDump
from gmweb.protocol.gmProtocol import pingboBetType

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.dataProbet = {}
        self.dataPingbo={}

@token_required
@asyncio.coroutine
def handleHttp(request: dict):
    """获取所有玩法"""
    objRep = cResp()

    try:
        with (yield from classSqlBaseMgr.getInstance(instanceName="probet_oss").objDbMysqlMgr) as conn:
            # 玩法
            sql = "select DISTINCT(playType) from dj_betresultbill"
            listRest = yield from conn.execute(sql)
            play_types = yield from listRest.fetchall()
            for i,x in enumerate(play_types):
                objRep.dataProbet[x[0]]=x[0]
            objRep.dataPingbo=pingboBetType
            return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)