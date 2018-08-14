import asyncio
import json
from datawrapper.sqlBaseMgr import classSqlBaseMgr
import logging
from error.errorCode import exceptionLogic, errorLogic
from gmweb.utils.tools import token_required, permission_required
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow


class cData():
    def __init__(self):
        self.accountId = ""

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []

@token_required
@permission_required('冻结名单查询')
@asyncio.coroutine
def handleHttp(request: dict):
    # 根据条件查询数据库冻结用户信息
    userId=request.get('userId','')
    email=request.get('email','')
    phone=request.get('phone','')
    guessUid=request.get('guessUid','')
    startTime=request.get('startTime',0)
    endTime=request.get('endTime',0)
    pn=request.get('pn',1)
    try:
        pn=int(pn)
        conn = classSqlBaseMgr.getInstance()
        sql=None
        if userId:
            sql = "select * from dj_account WHERE dj_account.accountId='{}' AND dj_account.status='1'".format(userId)

        if email:
            sql = "select * from dj_account WHERE dj_account.email='{}' AND dj_account.status='1'".format(email)

        if phone:
            sql = "select * from dj_account WHERE dj_account.phone='{}' AND dj_account.status='1'".format(phone)
        if guessUid:
            sql="select accountId from dj_bet WHERE dj_bet.guessUId='{}'".format(guessUid)
            listRest=yield from conn._exeCute(sql)
            res=yield from listRest.fetchone()
            if res is None:
                logging.debug(errorLogic.bet_hist_data_not_found)
                raise exceptionLogic(errorLogic.bet_hist_data_not_found)
            sql = "select * from dj_account WHERE dj_account.accountId='{}' AND dj_account.status='1'".format(res['accountId'])
        if sql is None:
            sql="select * from dj_account WHERE dj_account.status='1' AND dj_account.lockStartTime BETWEEN {} AND {} order by lockStartTime desc".format(startTime,endTime)

        listRest=yield from conn._exeCute(sql.replace(r'*','count(accountId)'))
        listCount=yield from listRest.fetchone()
        count=listCount[0]
        listRest = yield from conn._exeCute(sql+" limit {} offset {}".format(MSG_PAGE_COUNT,(pn-1)*MSG_PAGE_COUNT))
        users = yield from listRest.fetchall()
        if users is None:
            logging.debug(errorLogic.player_data_not_found)
            raise exceptionLogic(errorLogic.player_data_not_found)

        resp = cResp()
        for x in users:
            data = cData()
            data.accountId = x['accountId']
            data.lockStartTime=x['lockStartTime']
            data.lockEndTime=x['lockEndTime']
            data.lockReason=x['lockReason']
            data.level = x['level']
            resp.data.append(data)

        resp.count=count
        resp.ret = errorLogic.success[0]
        if pn==1:
            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "查询冻结账号信息",
                'actionTime': getNow(),
                'actionMethod': methodName,
                'actionDetail': "查询冻结账号:{},信息".format(userId),
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(resp)
    except exceptionLogic as e:
        logging.debug(e)
        raise e
    except Exception as e:
        logging.debug(e)
        raise exceptionLogic(errorLogic.db_error)


