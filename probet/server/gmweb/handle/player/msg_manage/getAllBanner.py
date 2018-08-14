import asyncio
import json
import logging
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from datawrapper.sqlBaseMgr import classSqlBaseMgr
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
    # 获取所有轮播图信息
    objRsp = cResp()
    try:
        sql = "select * from dj_banner ORDER BY dj_banner.index "
        result = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
        if result.rowcount <= 0:
            return classJsonDump.dumps(objRsp)
        else:
            dataList = []
            for var_row in result:
                dataDict = {}
                dataDict["index"] = var_row.index
                dataDict["title"] = var_row.title
                dataDict["image_url"] = var_row.image_url
                dataDict["link_url"] = var_row.link_url
                dataDict["update_time"] = var_row.update_time
                dataDict["addAccount"] = var_row.addAccount
                dataDict["id"] = var_row.id
                dataList.append(dataDict)
    except Exception as e:
        logging.exception(e)

    objRsp.data = dataList
    fileName = __name__
    nameList = fileName.split('.')
    methodName = nameList.pop()
    # 日志
    dictActionBill = {
        'billType': 'adminActionBill',
        'accountId': request.get('accountId', ''),
        'action': "查询所有轮播图",
        'actionTime': getNow(),
        'actionMethod': methodName,
        'actionDetail': "查询所有轮播图",
        'actionIp': request.get('srcIp', ''),
    }
    logging.getLogger('bill').info(json.dumps(dictActionBill))

    return classJsonDump.dumps(objRsp)

