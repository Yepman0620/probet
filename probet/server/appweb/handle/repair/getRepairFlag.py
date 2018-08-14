import asyncio
import logging
from lib.jsonhelp import classJsonDump
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from lib.timehelp import timeHelp
from error.errorCode import exceptionLogic, errorLogic


class cData():
    def __init__(self):
        self.repairFlag = 0
        self.surplus_time = 0


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@asyncio.coroutine
def handleHttp(dict_param: dict):
    """
    获取维护状态
    :param dict_param: json数据
    :return:
    """
    objRsp = cResp()
    objRsp.data = cData()

    platform = dict_param.get('platform', 1)
    if not platform:
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
            sql = "select start_time,end_time,repairFlag from dj_repair where repairFlag=1 and platform=%s"
            result = yield from conn.execute(sql, [platform])
            if result.rowcount <= 0:
                return classJsonDump.dumps(objRsp)
            else:
                for var_row in result:
                    start_time = var_row.start_time
                    end_time = var_row.end_time
                    repairFlag = var_row.repairFlag
                    surplus_time = end_time - timeHelp.getNow()
                    if (surplus_time < 0) or (start_time > timeHelp.getNow()):
                        surplus_time = 0
                        repairFlag = 0
                    objRsp.data.surplus_time = surplus_time
                    objRsp.data.repairFlag = repairFlag
                return classJsonDump.dumps(objRsp)
    except Exception as e:
        logging.exception(e)

