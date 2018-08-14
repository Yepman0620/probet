import asyncio
import json
import logging
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from lib.timehelp.timeHelp import getNow


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('轮播图管理')
@asyncio.coroutine
def handleHttp(request: dict):
    # 修改轮播图下标
    id_A = request.get('id_A', '')
    id_B = request.get('id_B', '')
    index_A = request.get('index_A', '')
    index_B = request.get('index_B', '')

    if not all([id_A, id_B, index_A, index_B]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        sql_A = "update dj_banner set dj_banner.index = {} where dj_banner.id = {}".format(index_B, id_A)
        sql_B = "update dj_banner set dj_banner.index = {} where dj_banner.id = {}".format(index_A, id_B)
        yield from classSqlBaseMgr.getInstance()._exeCuteCommit(sql_A)
        yield from classSqlBaseMgr.getInstance()._exeCuteCommit(sql_B)
        objResp=cResp()
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "修改轮播图下标",
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionDetail': "修改轮播图id：{},下标为：{},修改轮播图id：{},下标为：{}".format(id_A,index_A,id_B,index_B),
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return objResp
    except Exception as e:
        logging.exception(e)

