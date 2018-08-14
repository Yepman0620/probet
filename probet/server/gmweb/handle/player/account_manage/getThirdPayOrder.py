
import asyncio
from datawrapper.sqlBaseMgr import classSqlBaseMgr
import logging
from error.errorCode import exceptionLogic, errorLogic
from gmweb.protocol.gmProtocol import pingboBetType
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump


class cData():
    def __init__(self):
        self.retContent = ""

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = ""


@token_required
@permission_required('三方订单查询')
@asyncio.coroutine
def handleHttp(request: dict):
    # 根据条件查询数据库用户竞猜信息
    thirdPayOrder = request.get('thirdPayOrder', '')

    conn = classSqlBaseMgr.getInstance()
    sql = "select thirdPayName from dj_pay_order WHERE payOrder='{}'".format(thirdPayOrder)

    listRest = yield from conn._exeCute(sql)
    xx = yield from listRest.fetchone()
    #for var