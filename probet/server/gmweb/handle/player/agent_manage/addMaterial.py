import asyncio
import base64
import hashlib
import json
from gmweb.utils.models import tb_material
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from lib.aliyunoss import uploadDataFileToOss
from lib.jsonhelp import classJsonDump
from lib.timehelp import timeHelp
from datawrapper.sqlBaseMgr import classSqlBaseMgr
import logging
import uuid


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('推广素材管理')
@asyncio.coroutine
def handleHttp(request: dict):
    """新增推广素材"""
    objRep = cResp()

    bytesBase64Png = request.get("base64Png", "")
    imageSize = request.get("imageSize", "")

    if not all([bytesBase64Png, imageSize]):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    materialName = hashlib.md5(bytesBase64Png.encode()).hexdigest()
    imageData = base64.b64decode(bytesBase64Png[22:])
    dirPrefix = "material/"
    uploadDataFileToOss(imageData, dirPrefix, materialName + ".png")
    image_url = "http://probet-avator.oss-us-west-1.aliyuncs.com/{}{}.png".format(dirPrefix, materialName)
    imageId = str(uuid.uuid1())
    try:
        sql = tb_material.insert().values(
            imageId=imageId,
            image_url=image_url,
            imageSize=imageSize,
            create_time=timeHelp.getNow(),
            update_time=timeHelp.getNow()
        )
        yield from classSqlBaseMgr.getInstance()._exeCuteCommit(sql)

        sql = "select * from dj_material order by update_time desc"
        result = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
        if result.rowcount <= 0:
            return classJsonDump.dumps(objRep)
        else:
            for var in result:
                materialData = {}
                materialData['imageId'] = var.imageId
                materialData['image_url'] = var.image_url
                materialData['imageSize'] = var.imageSize
                objRep.data.append(materialData)
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "新增推广素材",
            'actionTime': timeHelp.getNow(),
            'actionMethod': methodName,
            'actionDetail': "新增推广素材imageId：{}".format(imageId),
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(objRep)

    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)

