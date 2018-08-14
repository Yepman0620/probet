import asyncio
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from lib.constants import DEPOSIT_LIST
from lib.jsonhelp import classJsonDump

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []

# @permission_required('充值明细')
@token_required
@asyncio.coroutine
def handleHttp(request: dict):
    # 获取所有支付方式
    resp=cResp()
    for x in DEPOSIT_LIST:
        resp.data.append(x.get('name'))

    resp.ret=errorLogic.success[0]
    return classJsonDump.dumps(resp)