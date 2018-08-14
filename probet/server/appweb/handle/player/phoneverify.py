from config import zoneConfig
import asyncio
import logging
import json
import random
from lib.phonesms import sendsmsverify
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic,errorLogic
from logic.regex import precompile
from logic.data.userData import classUserData


class cData():
    def __init__(self):
        self.iCode = ""
        self.phone = ""


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@asyncio.coroutine
def handleHttp(dict_param: dict):
    """绑定手机(银行卡)时获取验证码"""
    objRsp = cResp()

    strAccountId = dict_param.get("accountId", "")
    strPhone = dict_param.get('phoneNum', "")

    if strAccountId and strPhone:
        raise exceptionLogic(errorLogic.client_param_invalid)
    if strAccountId == "" and strPhone == "":
        raise exceptionLogic(errorLogic.client_param_invalid)
    if strAccountId:
        objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
        if objPlayerData is None:
            raise exceptionLogic(errorLogic.player_data_not_found)

        if objPlayerData.strPhone == "":
            raise exceptionLogic(errorLogic.player_telephone_is_not_bind)
        else:

            iCode = random.randint(1000, 9999)

            future = asyncio.get_event_loop().run_in_executor(None, sendsmsverify.send_sms, objPlayerData.strPhone, iCode)
            ret = yield from asyncio.wait_for(future, 10)

            logging.debug("send sms telephone{} response:".format(objPlayerData.strPhone) + str(ret))
            try:
                retDict = json.loads(ret)

                if retDict['Code'] != "OK":

                    if retDict['Code'] == "isv.BUSINESS_LIMIT_CONTROL":
                        return '{"ret":1,"retDes":"提醒|发送频率过高请稍后再试"}'.encode()
                    elif retDict['Code'] == "isv.BLACK_KEY_CONTROL_LIMIT":
                        return '{"ret":1,"retDes":"提醒|发送频率过高请稍后再试!"}'.encode()
                    elif retDict['Code'] == "isv.MOBILE_NUMBER_ILLEGAL":
                        return '{"ret":1,"retDes":"提醒|手机格式有误"}'.encode()
                    else:
                        return ('{"ret":1,"retDes":"提醒|%s"}' % (retDict['Message'])).encode()

                else:
                    yield from classDataBaseMgr.getInstance().setPhoneVerify(objPlayerData.strPhone, iCode)

            except Exception as e:
                logging.exception(e)
            # 构造回包
            objRsp.data = cData()
            objRsp.data.iCode = iCode
            return classJsonDump.dumps(objRsp)

    if strPhone:

        if precompile.TelePhoneRegex.search(strPhone) is None:
            raise exceptionLogic(errorLogic.player_telephone_invalid)
        iCode = random.randint(1000, 9999)

        future = asyncio.get_event_loop().run_in_executor(None, sendsmsverify.send_sms, strPhone, iCode)
        ret = yield from asyncio.wait_for(future, 10)

        logging.debug("send sms telephone{} response:".format(strPhone) + str(ret))
        try:
            retDict = json.loads(ret)

            if retDict['Code'] != "OK":

                if retDict['Code'] == "isv.BUSINESS_LIMIT_CONTROL":
                    return '{"ret":1,"retDes":"提醒|发送频率过高请稍后再试"}'.encode()
                elif retDict['Code'] == "isv.BLACK_KEY_CONTROL_LIMIT":
                    return '{"ret":1,"retDes":"提醒|发送频率过高请稍后再试!"}'.encode()
                elif retDict['Code'] == "isv.MOBILE_NUMBER_ILLEGAL":
                    return '{"ret":1,"retDes":"提醒|手机格式有误"}'.encode()
                else:
                    return ('{"ret":1,"retDes":"提醒|%s"}' % (retDict['Message'])).encode()

            else:

                yield from classDataBaseMgr.getInstance().setPhoneVerify(strPhone, iCode)

        except Exception as e:
            logging.exception(e)
            raise exceptionLogic(errorLogic.code_send_not_success)

        # 构造回包
        objRsp.data = cData()
        objRsp.data.iCode = iCode

        return classJsonDump.dumps(objRsp)


