from config import zoneConfig
import asyncio
import logging
import json
import random
from lib.phonesms import sendsmsverify
from lib.mailsms import sendmailsms
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic,errorLogic
from logic.regex import precompile
from logic.data.userData import classUserData


class cData():
    def __init__(self):
        self.iCode = ""


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""

@asyncio.coroutine
def handleHttp(dict_param: dict):
    """绑定邮箱时获取邮件验证码"""
    objRsp = cResp()

    try:
        strEmail = dict_param['email']
    except Exception as e:
        raise exceptionLogic(errorLogic.player_Email_is_none)

    if precompile.EmailRegex.search(strEmail) is None:
        raise exceptionLogic(errorLogic.player_Email_invalid)

    iCode = random.randint(1000, 9999)

    future = asyncio.get_event_loop().run_in_executor(None, sendmailsms.send_mail, strEmail, iCode)
    ret = yield from asyncio.wait_for(future, 10)

    logging.debug("send sms email{} response:".format(strEmail) + str(ret))

    yield from classDataBaseMgr.getInstance().setEmailVerify(strEmail, iCode)

    #构造回包
    objRsp.data = cData()
    objRsp.data.iCode = iCode

    return classJsonDump.dumps(objRsp)




