import asyncio
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from lib.tool import agent_token_required


class cData():
    def __init__(self):
        self.pc = []
        self.app = []


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@agent_token_required
@asyncio.coroutine
def handleHttp(request: dict):
    """获取域名"""
    objRep = cResp()

    try:
        sql = "select * from dj_domain"
        result = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
        if result.rowcount <= 0:
            return classJsonDump.dumps(objRep)
        else:
            pcDomainName = []
            appDomainName = []
            for var_row in result:
                if var_row.domainType == 'pc':
                    domainDict = {}
                    domainDict['domainId'] = var_row.domainId
                    domainDict['domainName'] = var_row.domainName
                    pcDomainName.append(domainDict)
                elif var_row.domainType == 'app':
                    domainDict = {}
                    domainDict['domainId'] = var_row.domainId
                    domainDict['domainName'] = var_row.domainName
                    appDomainName.append(domainDict)
            objRep.data = cData()
            objRep.data.pc = pcDomainName
            objRep.data.app = appDomainName
            return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)
        raise e

