import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.timehelp import timeHelp
import logging


class cData():
    def __init__(self):
        self.repairFlag = 0



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

    RepairFlag = yield from classDataBaseMgr.getInstance().getRepairFlag()
    if RepairFlag == "1":
        try:
            sql = "select dj_repair.start_time,dj_repair.end_time from dj_repair where dj_repair.repairFlag=1"
            result = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
            if not result.rowcount <= 0:
                for var_row in result:
                    start_time = var_row.start_time
                    end_time = var_row.end_time
        except Exception as e:
            logging.error(repr(e))

        surplus_time = end_time - timeHelp.getNow()

        if (surplus_time < 0) or (start_time > timeHelp.getNow()):
            surplus_time = 0
            RepairFlag = 0

        objRsp.data = cData()
        objRsp.data.repairFlag = RepairFlag
        objRsp.data.start_time = start_time
        objRsp.data.end_time = end_time
        objRsp.data.surplus_time = surplus_time

        return classJsonDump.dumps(objRsp)

    else:
        objRsp.data = cData()
        objRsp.data.repairFlag = RepairFlag
        return classJsonDump.dumps(objRsp)
