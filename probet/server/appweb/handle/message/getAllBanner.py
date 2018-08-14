import asyncio
import logging
from lib.jsonhelp import classJsonDump
from datawrapper.sqlBaseMgr import classSqlBaseMgr


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@asyncio.coroutine
def handleHttp(request: dict):
    # 获取所有轮播图信息
    objRsp = cResp()
    try:
        sql = "select dj_banner.index,dj_banner.title,dj_banner.image_url,dj_banner.link_url,dj_banner.id,dj_banner.update_time from dj_banner"
        result = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
        if result.rowcount <= 0:
            dataList = []
        else:
            dataList = []
            for var_row in result:
                dataDict = {}
                dataDict["index"] = var_row.index
                dataDict["title"] = var_row.title
                dataDict["image_url"] = var_row.image_url
                dataDict["link_url"] = var_row.link_url
                dataDict["id"] = var_row.id
                dataDict["update_time"] = var_row.update_time
                dataList.append(dataDict)
    except Exception as e:
        logging.exception(e)

    objRsp.data = dataList
    return classJsonDump.dumps(objRsp)

