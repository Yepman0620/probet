import asyncio
import json
from datawrapper.sqlBaseMgr import classSqlBaseMgr
import logging
from error.errorCode import errorLogic, exceptionLogic
from gmweb.utils.tools import token_required, permission_required
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow


class cData():
    def __init__(self):
        self.id = 0
        self.accountId = ""
        self.role_name = ""

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('用户管理')
@asyncio.coroutine
def handleHttp(request:dict):
    pn=request.get('pn',1)
    try:
        pn=int(pn)
        conn = classSqlBaseMgr.getInstance()
        sql = "select count(id) from dj_admin_account"
        listRest = yield from conn._exeCute(sql)
        count = yield from listRest.fetchone()

        sql = "select * from dj_admin_account ORDER BY dj_admin_account.id limit {} offset {}".format(MSG_PAGE_COUNT,(pn - 1) * MSG_PAGE_COUNT)
        listRest = yield from conn._exeCute(sql)
        accounts = yield from listRest.fetchall()

        resp=cResp()
        for x in accounts:
            data=cData()
            data.id=x['id']
            data.accountId=x['accountId']
            if x['role_id'] is None:
                data.role_name = ''
            else:
                sql = "select dj_admin_role.role_name from dj_admin_role WHERE dj_admin_role.id={}".format(x['role_id'])
                listRest = yield from conn._exeCute(sql)
                role_name = yield from listRest.fetchone()
                data.role_name = role_name[0]
            resp.data.append(data)

        resp.count=count[0]
        resp.ret=errorLogic.success[0]
        if pn==1:
            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "查询所有后台账号",
                'actionTime': getNow(),
                'actionMethod': methodName,
                'actionDetail': "查询所有后台账号",
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(resp)

    except Exception as e:
        logging.debug(e)
        raise exceptionLogic(errorLogic.db_error)
