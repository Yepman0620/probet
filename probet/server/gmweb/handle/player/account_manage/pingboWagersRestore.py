import asyncio
from gmweb.handle.pinbo.check_pingbo_wagers import todo_pingbo_wagers
from gmweb.handle.pinbo.wagers import get_wagers
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
import logging

from lib.timehelp.timeHelp import getNow


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.add_count = 0
        self.update_count=0

@token_required
@permission_required('平博注单恢复')
@asyncio.coroutine
def handleHttp(request: dict):
    userId = request.get('userId', '')
    startTime = request.get('startTime', 0)
    endTime=request.get('endTime',0)
    if not userId:
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        res=yield from get_wagers(startTime,endTime,userId)
        add_count=0
        update_count=0
        total_count=len(res)
        for x in res:
            ret=yield from todo_pingbo_wagers(x)
            if ret[0] is True:
                if ret[1]=='add':
                    add_count+=1
                else:
                    update_count+=1
        resp=cResp()
        resp.update_count=update_count
        resp.add_count=add_count
        resp.total_count=total_count
        return classJsonDump.dumps(resp)
    except Exception as e:
        logging.debug(repr(e))
        raise e

