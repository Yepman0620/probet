import asyncio
import json
import logging
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from logic.data.userData import classRepairData
import uuid
from lib.timehelp import timeHelp
from gmweb.utils.tools import token_required, permission_required
from datawrapper.pushDataOpWrapper import pushPinboRepairData

class cData():
    def __init__(self):
        self.start = 0
        self.end = 0
        self.repairFlag = 0
        self.reapirId = ""


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
    维护管理
    :param dict_param: json数据
    :return:
    """
    objRsp = cResp()

    strAccountId=dict_param.get('accountId')
    startTime = dict_param.get("start", 0)
    endTime = dict_param.get("end", 0)
    RepairFlag = dict_param.get("repairFlag", 0)
    RepairId = dict_param.get("repairId", "")
    platform = dict_param.get("platform", 1)
    if not all([startTime, endTime]):
        raise exceptionLogic(errorLogic.client_param_invalid)
    repairData = classRepairData()
    if len(RepairId) <= 0:
        repairData.strRepairId = str(uuid.uuid1())
    else:
        repairData.strRepairId = RepairId
    repairData.iTime = timeHelp.getNow()
    repairData.iStartTime = startTime
    repairData.iEndTime = endTime
    repairData.iRepairFlag = RepairFlag
    repairData.strAccountId = strAccountId
    repairData.iTimeOfUse = endTime - startTime
    repairData.iPlatform = platform

    yield from classDataBaseMgr.getInstance().addRepairData(repairData, RepairId)
    surplus_time = endTime - timeHelp.getNow()

    yield from pushPinboRepairData(endTime,RepairFlag,0 if surplus_time < 0 else surplus_time,startTime,"broadCastPub")

    objRsp.data = cData()
    objRsp.data.reapirId = repairData.strRepairId
    objRsp.data.start = repairData.iStartTime
    objRsp.data.end = repairData.iEndTime
    objRsp.data.repairFlag = RepairFlag
    objRsp.data.platform = repairData.iPlatform
    yield from asyncio.sleep(1)
    fileName = __name__
    nameList = fileName.split('.')
    methodName = nameList.pop()
    # 日志
    dictActionBill = {
        'billType': 'adminActionBill',
        'accountId': dict_param.get('accountId', ''),
        'action': "第三方维护状态修改",
        'actionTime': timeHelp.getNow(),
        'actionMethod': methodName,
        'actionDetail': "第三方维护状态修改",
        'actionIp': dict_param.get('srcIp', ''),
    }
    logging.getLogger('bill').info(json.dumps(dictActionBill))
    return classJsonDump.dumps(objRsp)
