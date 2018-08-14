import asyncio
import logging
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from logic.logicmgr.checkParamValid import checkIsInt


class cData():
    def __init__(self):
        self.msgId = ''
        self.title = ''
        self.detail = ''
        self.msgTime = 0
        self.receiver = 0


class cResp():
    def __init__(self):
        self.count=0
        self.ret = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('系统消息发送')
@asyncio.coroutine
def handleHttp(dict_param: dict):
    """
    后台查询历史系统消息
    """
    objRsp = cResp()

    pn = dict_param.get("pn", 1)
    if not checkIsInt(pn):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    conn=classSqlBaseMgr.getInstance()
    # 去重获取msgId
    sql="select distinct msgId from dj_all_msg WHERE type=0 "
    listRest=yield from conn._exeCute(sql)
    msgIds=yield from listRest.fetchall()
    if len(msgIds)==0:
        return classJsonDump.dumps(objRsp)
    else:
        ids=[]
        for x in msgIds:
            ids.append(x[0])

    # 根据id获取消息
    for x in msgIds:
        sql="select * from dj_all_msg WHERE msgId='{}' ".format(x[0])
        listRest=yield from conn._exeCute(sql)
        msgs=yield from listRest.fetchall()
        if len(msgs)==0:
            return classJsonDump.dumps(objRsp)

        if len(msgs)>5:
            #全体发送
            data = cData()
            data.msgId=msgs[0]['msgId']
            data.msgTime=msgs[0]['msgTime']
            data.detail=msgs[0]['msgDetail']
            data.title=msgs[0]['msgTitle']
            data.sendFrom = msgs[0]['sendFrom']
            data.receiver='全体'
            objRsp.data.append(data)
            continue
        else:
            for x in msgs:
                data=cData()
                data.msgId = x['msgId']
                data.msgTime = x['msgTime']
                data.detail = x['msgDetail']
                data.title = x['msgTitle']
                data.receiver = x['sendTo']
                data.sendFrom=x['sendFrom']
                objRsp.data.append(data)
    objRsp.count=len(objRsp.data)
    objRsp.data=sorted(objRsp.data,key=lambda data: data.msgTime,reverse=True)
    objRsp.data=objRsp.data[(pn-1)*MSG_PAGE_COUNT:pn*MSG_PAGE_COUNT:]
    return classJsonDump.dumps(objRsp)

