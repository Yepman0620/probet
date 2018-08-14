import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.tools import token_required, permission_required


class cData():
    def __init__(self):
        self.count = 0
        self.repairingData = []
        self.repairedData = []


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
    维护记录
    :param dict_param: json数据
    :return:
    """
    objRsp = cResp()

    iPageNum = int(dict_param.get("pageNum", 1))

    RepairedDataList, RepairingDataList = yield from classSqlBaseMgr.getInstance().getRepairData(iPageNum)
    count = yield from classSqlBaseMgr.getInstance().getRepairedCount()
    objRsp.data = cData()
    objRsp.data.count = count
    objRsp.data.repairingData = RepairingDataList
    objRsp.data.repairedData = RepairedDataList

    return classJsonDump.dumps(objRsp)
