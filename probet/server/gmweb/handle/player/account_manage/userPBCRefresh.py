import asyncio
from gmweb.handle.pinbo.get_player_info import get_pingbo_player_info
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
import logging

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.coin = 0

@token_required
@permission_required('用户列表查询')
@asyncio.coroutine
def handleHttp(request: dict):
    userId = request.get('userId', '')

    if not userId:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        res=yield from get_pingbo_player_info(userId)
        resp=cResp()
        resp.coin=res['availableBalance']
        return classJsonDump.dumps(resp)
    except Exception as e:
        logging.error(repr(e))
        raise e


