import asyncio
import json
import logging
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow


class cData():
    def __init__(self):
        self.id = ""
        self.name = ""
        self.accountId = ""
        self.bank = ""
        self.status = ""
        self.kind = ""


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('线下充值账户管理')
@asyncio.coroutine
def handleHttp(request: dict):
    # 更新线下充值账户
    objRsp = cResp()
    name=request.get('name','')
    cardId=request.get('cardId','')
    branch=request.get('branch','')
    id = request.get('id', '')
    status = request.get('status', '')
    bank=request.get('bank','')
    action=request.get('action','')
    if not all([id,action]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    if action not in ['status','more']:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        if action=='status':
            if not status:
                logging.debug(errorLogic.client_param_invalid)
                raise exceptionLogic(errorLogic.client_param_invalid)
            sql = "update dj_offline_account_recharge set status = {} where dj_offline_account_recharge.id = {}".format(status,id)
        else:
            if not all([name,cardId]):
                logging.debug(errorLogic.client_param_invalid)
                raise exceptionLogic(errorLogic.client_param_invalid)
            sql = "update dj_offline_account_recharge set name='{}',accountId='{}',bank='{}',bankInfo='{}' WHERE id={}".format(
                name, cardId,bank,branch,id)
        yield from classSqlBaseMgr.getInstance()._exeCuteCommit(sql)
        select_sql = "select * from dj_offline_account_recharge"
        result = yield from classSqlBaseMgr.getInstance()._exeCute(select_sql)
        if result.rowcount <= 0:
            return b'0'
        else:
            dataList = []
            for var_row in result:
                dataDict = {}
                dataDict["id"] = var_row.id
                dataDict["name"] = var_row.name
                dataDict["accountId"] = var_row.accountId
                dataDict["bank"] = var_row.bank
                dataDict["status"] = var_row.status
                dataDict["bankInfo"]=var_row.bankInfo
                dataDict["kind"]=var_row.kind
                dataList.append(dataDict)

        objRsp.data = dataList
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "修改线下充值账号状态",
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionDetail': "修改线下充值id为:{} 的账号状态（{}）".format(id,"上线" if status==0 else "暂停使用"),
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(objRsp)
    except Exception as e:
        logging.debug(e)
        raise exceptionLogic(errorLogic.db_error)

