import asyncio
import base64
import hashlib
import json
from gmweb.utils.models import tb_banner
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from lib.aliyunoss import uploadDataFileToOss
from lib.jsonhelp import classJsonDump
from lib.timehelp import timeHelp
from datawrapper.sqlBaseMgr import classSqlBaseMgr
import logging


class cData():
    def __init__(self):
        self.id = ""
        self.image_url = ""
        self.index = ""
        self.link_url = ""
        self.title = ""


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('轮播图管理')
@asyncio.coroutine
def handleHttp(request: dict):
    # 更新轮播图信息
    bannerId = request.get('bannerId')
    title = request.get('title', '')
    link_url = request.get('link_url', '')
    bytesBase64Png = request.get("base64Png", "")

    if not bannerId:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    if bytesBase64Png:
        bannerName = hashlib.md5(bytesBase64Png.encode()).hexdigest()
        imageData = base64.b64decode(bytesBase64Png[22:])
        dirPrefix = "banner/"
        image_url = "http://probet-avator.oss-us-west-1.aliyuncs.com/{}{}.png".format(dirPrefix, bannerName)
        uploadDataFileToOss(imageData, dirPrefix, bannerName + ".png")
        sql = "update dj_banner set title='{}',link_url='{}',image_url='{}' WHERE id={} ".format(title, link_url,image_url, bannerId)
    else:
        sql = "update dj_banner set title='{}',link_url='{}' WHERE id={} ".format(title, link_url, bannerId)

    conn=classSqlBaseMgr.getInstance()
    try:
        yield from conn._exeCuteCommit(sql)

        sql="select * from dj_banner"
        listRest=yield from conn._exeCute(sql)
        banners=yield from listRest.fetchall()
        objRsp=cResp()
        if len(banners) == 0:
            return classJsonDump.dumps(objRsp)
        else:
            for var_row in banners:
                dataDict = cData()
                dataDict.index = var_row['index']
                dataDict.title = var_row['title']
                dataDict.image_url = var_row['image_url']
                dataDict.link_url = var_row['link_url']
                dataDict.update_time = var_row['update_time']
                dataDict.addAccount = var_row['addAccount']
                dataDict.id = var_row['id']
                objRsp.data.append(dataDict)

        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "修改轮播图信息",
            'actionTime': timeHelp.getNow(),
            'actionMethod': methodName,
            'actionDetail': "修改轮播图信息Id：{}".format(bannerId),
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(objRsp)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)

