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

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('轮播图管理')
@asyncio.coroutine
def handleHttp(request: dict):
    # 新增轮播图信息
    accountId = request.get('accountId')
    title = request.get('title', '')
    bytesBase64Png = request.get("base64Png", "")
    link_url = request.get('link_url', '')
    if not all([title, bytesBase64Png]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    bannerName = hashlib.md5(bytesBase64Png.encode()).hexdigest()
    imageData = base64.b64decode(bytesBase64Png[22:])
    dirPrefix = "banner/"
    uploadDataFileToOss(imageData, dirPrefix, bannerName + ".png")

    try:
        sql = "select dj_banner.index from dj_banner"
        listRest = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
        listRest=yield from listRest.fetchall()
        if len(listRest) == 0:
            index = 0
        else:
            sql="select max(dj_banner.index) from dj_banner"
            ret = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
            ret = yield from ret.fetchone()
            index = ret[0] + 1

        sql = tb_banner.insert().values(
            index=index,
            link_url=link_url,
            image_url="http://probet-avator.oss-us-west-1.aliyuncs.com/{}{}.png".format(dirPrefix, bannerName),
            title=title,
            addAccount=accountId,
            create_time=timeHelp.getNow(),
            update_time=timeHelp.getNow()
        )
        yield from classSqlBaseMgr.getInstance()._exeCuteCommit(sql)
        objResp=cResp()
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "新增轮播图",
            'actionTime': timeHelp.getNow(),
            'actionMethod': methodName,
            'actionDetail': "新增轮播图，标题：{}".format(title),
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(objResp)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)

