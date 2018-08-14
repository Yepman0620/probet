import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic
from lib.tool import agent_token_required
from config.vipConfig import vip_config
from lib.timehelp import timeHelp


class cData():
    def __init__(self):
        self.agentId = ""
        self.realName = ""
        self.phoneNum = ""
        self.email = ""
        self.count = 0



class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@agent_token_required
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """个人信息"""
    objRsp = cResp()

    agentId = dict_param.get("agentId", "")
    objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(agentId)
    objAgentData = yield from classDataBaseMgr.getInstance().getAgentData(agentId)
    allAccountNum = yield from classSqlBaseMgr.getInstance().getAccountCountByAgent(agentId)
    unReadNum = yield from classSqlBaseMgr.getInstance().getAgentMsgUnReadNum(agentId)

    # 构造回包
    objRsp.data = cData()
    objRsp.data.agentId = agentId
    objRsp.data.realName = objPlayerData.strRealName
    objRsp.data.phoneNum = objPlayerData.strPhone
    objRsp.data.email = objPlayerData.strEmail
    objRsp.data.count = allAccountNum
    objRsp.data.balance = objPlayerData.iCoin
    objRsp.data.loginTime = objPlayerData.iLastLoginTime
    objRsp.data.cid = objAgentData.iCid
    objRsp.data.unReadNum = unReadNum

    return classJsonDump.dumps(objRsp)
