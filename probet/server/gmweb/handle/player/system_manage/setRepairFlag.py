import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from logic.data.userData import classRepairData
import uuid
from lib.timehelp import timeHelp
from gmweb.utils.tools import token_required, permission_required

class cData():
    def __init__(self):
        self.repairFlag = 0



class cResp():
    def __init__(self):

        self.ret = 0
        self.retDes = ""
        self.data = ""


@token_required
@permission_required('平博维护管理')
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """
    设置维护状态
    :param dict_param: json数据
    :return:
    """
    objRsp = cResp()

    RepairFlag = dict_param.get("repairFlag", 0)
    if not RepairFlag:
        objRsp.data = cData()
        return classJsonDump.dumps(objRsp)
    else:
        yield from classDataBaseMgr.getInstance().setRepairFlag(RepairFlag)

    objRsp.data = cData()
    objRsp.data.repairFlag = RepairFlag
    return classJsonDump.dumps(objRsp)
