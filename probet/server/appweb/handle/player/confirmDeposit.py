import asyncio
import logging
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib import certifytoken
from lib.jsonhelp import classJsonDump
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from lib.tool import user_token_required


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """存款"""
    objRsp = cResp()

    orderId = dict_param.get("orderId", "")
    try:
        with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
            sql = "update dj_pay_order set status=2 where payOrder=%s"
            yield from conn.execute(sql, [orderId])
    except Exception as e:
        logging.error(repr(e))
        raise exceptionLogic(errorLogic.db_error)

    return classJsonDump.dumps(objRsp)


