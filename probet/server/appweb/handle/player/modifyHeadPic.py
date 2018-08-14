import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
import logging
from lib import certifytoken
import hashlib
import base64
#import aiofiles
from appweb.proc import procVariable
from appweb import appweb_config
from lib.aliyunoss import uploadDataFileToOss
from lib.tool import user_token_required


class cData():
    def __init__(self):
        self.headAddress = ""


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """修改头像"""
    objRsp = cResp()

    strAccountId = dict_param.get("accountId", "")
    bytesBase64Png = dict_param.get("base64Png", "")
    if not bytesBase64Png:
        raise exceptionLogic(errorLogic.client_param_invalid)
    objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
    try:
        avatorName = hashlib.md5(bytesBase64Png.encode()).hexdigest()
        imageData = base64.b64decode(bytesBase64Png[22:])
        #objFileHandle = yield from aiofiles.open("/var/www/html/avator/" + avatorName + ".png", "wb")
        #yield from objFileHandle.write(imageData)
        #yield from objFileHandle.close()
        dirPrefix = "avator/"
        uploadDataFileToOss(imageData, dirPrefix, avatorName + ".png")

    except Exception as e:
        logging.exception(e)
    if procVariable.debug:
        objPlayerData.strHeadAddress = "http://probet-avator.oss-us-west-1.aliyuncs.com/{}{}.png".format(dirPrefix,avatorName)
    else:
        objPlayerData.strHeadAddress = "http://probet-avator.oss-us-west-1.aliyuncs.com/{}{}.png".format(dirPrefix,avatorName)
    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)
    # 构造回包
    objRsp.data = cData()
    objRsp.data.headAddress = objPlayerData.strHeadAddress

    return classJsonDump.dumps(objRsp)
