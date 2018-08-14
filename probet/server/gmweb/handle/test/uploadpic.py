import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
import datetime, random, os
from io import StringIO
import logging
import hashlib
import base64
#import aiofiles
from appweb.proc import procVariable
from appweb import appweb_config
from lib.aliyunoss import uploadDataFileToOss


class cResp():
    def __init__(self):
        self.error = ""
        self.url = ""
        self.uploaded = 1
        self.fileName = ""

@asyncio.coroutine
def handleHttp(dict_param: dict):
    """CKEditor上传图片"""
    objRsp = cResp()
    objFile = dict_param["upload"]
    #读取文件的raw 数据
    try:
        bytesPicData = objFile.file.read()
        strPicName = hashlib.md5(bytesPicData).hexdigest()
        dirPrefix = 'upload/'
        uploadDataFileToOss(bytesPicData, dirPrefix, strPicName + ".png")
    except Exception as e:
        logging.exception(e)

    objRsp.url = "http://probet-avator.oss-us-west-1.aliyuncs.com/{}{}.png".format(dirPrefix, strPicName)
    objRsp.fileName = strPicName

    return classJsonDump.dumps(objRsp)

