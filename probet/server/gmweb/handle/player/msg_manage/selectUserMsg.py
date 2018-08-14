import asyncio
import json
import logging

import time

from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.tools import token_required, permission_required
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow


class cResp():
    def __init__(self):
        self.ret = 0
        self.count = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('邮件查询')
@asyncio.coroutine
def handleHttp(request: dict):
    # 根据条件查询数据库用户邮件信息
    objRep = cResp()
    msgList = []

    userId = request.get('userId', '')
    phone = request.get('phone', '')
    email = request.get('email', '')
    startTime = request.get('startTime', 0)
    endTime = request.get('endTime', 0)
    pn = request.get('pn', 1)
    try:
        pn = int(pn)
    except Exception as e:
        logging.debug(e)
        raise exceptionLogic(errorLogic.client_param_invalid)
    try:
        accountId=None
        if userId:
            accountId = userId
        elif phone:
            sql = "select dj_account.accountId from dj_account where dj_account.phone = '{}' ".format(phone)
            result = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
            if result.rowcount <= 0:
                return classJsonDump.dumps(objRep)
            else:
                for var_row in result:
                    accountId = var_row.accountId
        elif email:
            sql = "select dj_account.accountId from dj_account where dj_account.email = '{}' ".format(email)
            result = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
            if result.rowcount <= 0:
                return classJsonDump.dumps(objRep)
            else:
                for var_row in result:
                    accountId = var_row.accountId

        if (not startTime) and (not endTime):
            #没传时间
            logging.debug(errorLogic.client_param_invalid)
            raise exceptionLogic(errorLogic.client_param_invalid)
        else:
            sql = "select dj_all_msg.msgId,dj_all_msg.msgTime,dj_all_msg.msgTitle,dj_all_msg.msgDetail,dj_all_msg.sendFrom from dj_all_msg where dj_all_msg.sendTo = '{}' and (dj_all_msg.msgTime between {} and {}) order by dj_all_msg.msgTime desc limit {} offset {}".format(
                accountId, startTime, endTime, 10, (pn-1) * 10)
            if accountId is None:
                sql = "select dj_all_msg.msgId,dj_all_msg.msgTime,dj_all_msg.msgTitle,dj_all_msg.msgDetail,dj_all_msg.sendFrom from dj_all_msg where dj_all_msg.msgTime between {} and {} order by dj_all_msg.msgTime desc limit {} offset {}".format(
                    startTime, endTime, 10, (pn-1) * 10)
            ret_msg = yield from classSqlBaseMgr.getInstance()._exeCute(sql)
            if ret_msg.rowcount <= 0:
                return classJsonDump.dumps(objRep)
            else:
                for var_row in ret_msg:
                    msgDict = {}
                    msgDict["msgId"] = var_row.msgId
                    msgDict["msgTime"] = var_row.msgTime
                    msgDict["msgTitle"] = var_row.msgTitle
                    msgDict["msgDetail"] = var_row.msgDetail
                    msgDict["sendFrom"] = var_row.sendFrom
                    msgList.append(msgDict)
            sql_count = "select count(dj_all_msg.msgId) from dj_all_msg where dj_all_msg.sendTo = '{}' and (dj_all_msg.msgTime between {} and {})".format(
                accountId, startTime, endTime)
            if accountId is None:
                sql_count = "select count(dj_all_msg.msgId) from dj_all_msg where dj_all_msg.msgTime between {} and {}".format(startTime, endTime)
            ret_count = yield from classSqlBaseMgr.getInstance()._exeCute(sql_count)
            if ret_count.rowcount <= 0:
                objRep.count = 0
            else:
                for var_row in ret_count:
                    objRep.count = var_row[0]

    except Exception as e:
        logging.debug(repr(e))
        raise exceptionLogic(errorLogic.db_error)
    if pn==1:
        fileName = __name__
        nameList = fileName.split('.')
        methodName = nameList.pop()
        # 日志
        dictActionBill = {
            'billType': 'adminActionBill',
            'accountId': request.get('accountId', ''),
            'action': "查询用户邮件信息",
            'actionTime': getNow(),
            'actionMethod': methodName,
            'actionDetail': "查询用户：{} 邮件信息".format(accountId),
            'actionIp': request.get('srcIp', ''),
        }
        logging.getLogger('bill').info(json.dumps(dictActionBill))

    objRep.data = msgList
    return classJsonDump.dumps(objRep)
