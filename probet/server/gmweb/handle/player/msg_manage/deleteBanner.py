import asyncio
import json
import logging
from error.errorCode import exceptionLogic, errorLogic
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
    # 删除轮播图信息
    objRsp = cResp()

    id = request.get('id', '')
    if not id:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        sql = "select dj_banner.index from dj_banner where dj_banner.id={}".format(id)
        ret = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
        ret=yield from ret.fetchone()
        if len(ret)==0:
            logging.debug(errorLogic.data_not_valid)
            raise exceptionLogic(errorLogic.data_not_valid)
        index = ret[0]

        sql = "delete from dj_banner where dj_banner.id = {}".format(id)
        yield from classSqlBaseMgr.getInstance()._exeCuteCommit(sql)

        sql = "select dj_banner.index,dj_banner.id from dj_banner where dj_banner.index > {}".format(index)
        retList = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
        retList=yield from retList.fetchall()
        if retList is None:
            try:
                sql = "select * from dj_banner"
                result = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
                result=yield from result.fetchall()
                if len(result)== 0:
                    return classJsonDump.dumps(objRsp)
                else:
                    dataList = []
                    for var_row in result:
                        dataDict = {}
                        dataDict["index"] = var_row['index']
                        dataDict["title"] = var_row['title']
                        dataDict["image_url"] = var_row['image_url']
                        dataDict["link_url"] = var_row['link_url']
                        dataDict["update_time"] = var_row['update_time']
                        dataDict["addAccount"] = var_row['addAccount']
                        dataDict["id"] = var_row['id']
                        dataList.append(dataDict)
            except Exception as e:
                logging.exception(e)
        for var_row in retList:
            index = var_row[0] - 1
            id = var_row[1]
            sql = "update dj_banner set dj_banner.index={} where dj_banner.id={} ".format(index, id)
            yield from classSqlBaseMgr.getInstance()._exeCuteCommit(sql)

        sql = "select * from dj_banner"
        result = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
        result=yield result.fetchall()
        if len(result) == 0:
            return classJsonDump.dumps(objRsp)
        else:
            dataList = []
            for var_row in result:
                dataDict = {}
                dataDict["index"] = var_row['index']
                dataDict["title"] = var_row['title']
                dataDict["image_url"] = var_row['image_url']
                dataDict["link_url"] = var_row['link_url']
                dataDict["update_time"] = var_row['update_time']
                dataDict["addAccount"] = var_row['addAccount']
                dataDict["id"] = var_row['id']
                dataList.append(dataDict)
        objRsp.data = dataList
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "删除轮播图",
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionDetail': "删除轮播图id：{}".format(id),
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(objRsp)
    except Exception as e:
        logging.exception(e)



