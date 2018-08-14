import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib import certifytoken
from lib.tool import user_token_required


class cAccountBaseData():
    def __init__(self):
        self.realName = ""
        self.sex = ""
        self.born = ""
        self.address = ""


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@user_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """设置基本信息"""
    objRsp = cResp()

    strAccountId = dict_param.get('accountId','')
    strRealName = dict_param.get('realName')
    strSex = dict_param.get('sex','')
    strBorn = dict_param.get('born','')
    if not all([strRealName,strSex,strBorn]):
        raise exceptionLogic(errorLogic.client_param_invalid)

    objPlayerData,objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
    if objPlayerData.strRealName:
        raise exceptionLogic(errorLogic.client_param_invalid)

    objPlayerData.strRealName = strRealName
    objPlayerData.strSex = strSex
    objPlayerData.strBorn = strBorn
    objPlayerData.dictAddress = dict_param.get('address','')
    yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objLock)

    # 构造回包
    objRsp.data = cAccountBaseData()
    objRsp.data.realName = objPlayerData.strRealName
    objRsp.data.sex = objPlayerData.strSex
    objRsp.data.born = objPlayerData.strBorn
    objRsp.data.address = objPlayerData.dictAddress

    return classJsonDump.dumps(objRsp)
