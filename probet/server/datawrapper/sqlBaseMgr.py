import threading
import asyncio
from aiomysql.sa import create_engine
from dbsvr.logic import match_flush
from error.errorCode import errorLogic, exceptionLogic
from lib.timehelp import timeHelp
import logging
import time

class classSqlBaseMgr():


    _instance = {}
    _instance_lock = threading.Lock()
    _defaultInstance = "default"

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            #if not hasattr(cls, "_instance") or "__instanceName__" in kwargs:
            if "__instanceName__" in kwargs:
                objInstance = cls.getInstance(kwargs["__instanceName__"])
            else:
                objInstance = cls.getInstance(cls._defaultInstance)

            if objInstance is None:
                objNew = object.__new__(cls)
                # objNew.__init__(*args, **kwargs)
                objNew.__init__()
                # 拥有多个单例对象
                if "__instanceName__" in kwargs:
                    cls._instance[kwargs["__instanceName__"]] = objNew
                else:
                    cls._instance[cls._defaultInstance] = objNew

        return cls._instance

    @classmethod
    def getInstance(cls, instanceName=None):
        if instanceName is None:
            return cls._instance.get(cls._defaultInstance,None)
        else:
            return cls._instance.get(instanceName,None)

    def __init__(self):

        self.objDbMysqlMgr = None

    @asyncio.coroutine
    def connetSql(self,host,port,user,password,db,loop,charset="utf8"):

        self.objDbMysqlMgr = yield from create_engine(host=host, port=port,
                                                      user=user, password=password,
                                                      db=db,
                                                      loop=loop, charset=charset,autocommit=True)

    def getEngine(self):
        return self.objDbMysqlMgr

    def __del__(self):
        pass

    @asyncio.coroutine
    def _exeCute(self, sql=''):
    # 针对读操作返回结果集
        try:
            with (yield from self.objDbMysqlMgr) as conn:
                result=yield from conn.execute(sql)
                return result

        except Exception as e :
            logging.debug(e)
            raise exceptionLogic(errorLogic.db_error)

    @asyncio.coroutine
    def _exeCuteCommit(self, sql=''):
    # 针对更新,删除,事务等操作失败时回滚
        try:
            with (yield from self.objDbMysqlMgr) as conn:
                yield from conn.execute(sql)
        except Exception as e:
            logging.debug(e)
            raise exceptionLogic(errorLogic.db_error)

    @asyncio.coroutine
    def getLiveMatchData(self):

        with (yield from self.objDbMysqlMgr) as conn:
            result = yield from conn.execute(match_flush.getLiveMatchDataSql())
            if result.rowcount <= 0:
                return []
            else:
                retList = []
                for var_row in result:
                    retList.append(var_row.matchId)
                return retList

    @asyncio.coroutine
    def getAllMatchIds(self):

        with (yield from self.objDbMysqlMgr) as conn:
            result = yield from conn.execute(match_flush.getAllMatchDataSql())
            if result.rowcount <= 0:
                return []
            else:
                retList = []
                for var_row in result:
                    retList.append(var_row.matchId)

                return retList

    @asyncio.coroutine
    def getTodayMatchIds(self):

        with (yield from self.objDbMysqlMgr) as conn:
            result = yield from conn.execute(match_flush.getTodayMatchDataSql())
            if result.rowcount <= 0:
                return []
            else:
                retList = []
                for var_row in result:
                    retList.append(var_row.matchId)

                return retList

    @asyncio.coroutine
    def getNotBeginMatchIds(self):

        with (yield from self.objDbMysqlMgr) as conn:
            result = yield from conn.execute(match_flush.getNotBeginMatchDataSql())
            if result.rowcount <= 0:
                return []
            else:
                retList = []
                for var_row in result:
                    retList.append(var_row.matchId)
                return retList


    @asyncio.coroutine
    def getMatchStateCount(self):

        with (yield from self.objDbMysqlMgr) as conn:
            result = yield from conn.execute("select dj_match.matchState, count(0) from dj_match group by dj_match.matchState")
            if result.rowcount <= 0:
                return []
            else:
                retList = []
                for var_row in result:
                    #print(dir(var_row))
                    retList.append({"matchState":var_row.get("matchState"),"count":var_row.get("count(0)")})
                return retList


    @asyncio.coroutine
    def getGuessBetHistory(self,accountId:str):

        with (yield from self.objDbMysqlMgr) as conn:
            sql = "select dj_bet.guessUId from dj_bet where dj_bet.accountId = %s and dj_bet.result = '' order by dj_bet.time desc"
            result = yield from conn.execute(sql,[accountId])
            print(sql)
            if result.rowcount <= 0:
                return []
            else:
                retList = []
                for var_row in result:
                    #print(dir(var_row))
                    retList.append(var_row.guessUId)
                return retList

    @asyncio.coroutine
    def getGuessResultHistory(self,accountId: str):

        with (yield from self.objDbMysqlMgr) as conn:
            result = yield from conn.execute("select dj_bet.guessUId from dj_bet where  dj_bet.accountId = %s "
                                             "and dj_bet.result != '' and dj_bet.time > %s order by dj_bet.time desc",[accountId,timeHelp.getNow() - 86400])
            if result.rowcount <= 0:
                return []
            else:
                retList = []
                for var_row in result:
                    # print(dir(var_row))
                    retList.append(var_row.guessUId)
                return retList

    @asyncio.coroutine
    def getBetHistoryAllNum(self, timeRange, accountId):
        with (yield from self.objDbMysqlMgr) as conn:
            sql = "select count(dj_bet.guessUId) as total from dj_bet where dj_bet.accountId = %s and dj_bet.time > %s order by dj_bet.time desc"

            #print(sql)
            result = yield from conn.execute(sql,[accountId, timeHelp.getNow() - timeRange * 86400])
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    # print(repr(var_row))
                    """
                    mysql> select count(dj_bet.guessUId) as total ,sum(dj_bet.betCoin) as waterCoin,sum(dj_bet.winCoin) as winCoin,count(dj_bet.resultId != '') as winCount from dj_bet where dj_bet.accountId = 'tiger888' and (dj_bet.time between now() and date_sub(now(),interval -1 day)) order by dj_bet.time;
                    +-------+-----------+---------+----------+
                    | total | waterCoin | winCoin | winCount |
                    +-------+-----------+---------+----------+
                    |     1 |        10 |       0 |        1 |
                    +-------+-----------+---------+----------+
                    """
                    return var_row.total

    @asyncio.coroutine
    def getPinBoBetHistoryAllNum(self, timeRange, accountId):
        with (yield from self.objDbMysqlMgr) as conn:
            sql = "select count(dj_pinbo_wagers.wagerId) as total from dj_pinbo_wagers where dj_pinbo_wagers.loginId = %s and dj_pinbo_wagers.wagerDateFm > %s order by dj_pinbo_wagers.wagerDateFm desc"

            # print(sql)
            result = yield from conn.execute(sql, ["probet."+accountId, timeHelp.getNow() - timeRange * 86400])
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    return var_row.total

    @asyncio.coroutine
    def getBetHistoryAllWaterWinSum(self, timeRange, accountId):
        with (yield from self.objDbMysqlMgr) as conn:
            sql = "select count(dj_bet.guessUId) as total ,sum(dj_bet.betCoin) as waterCoin,sum(dj_bet.winCoin) as winCoin,count(dj_bet.result != '') as winCount from dj_bet where dj_bet.accountId = %s and dj_bet.time > %s "
            # print(sql)
            sql_winCount = "select count(guessUid) as winCount from dj_bet where accountId=%s and result!='' and dj_bet.time > %s "
            ret = yield from conn.execute(sql_winCount,[accountId,timeHelp.getNow() - timeRange * 86400])
            if ret.rowcount<=0:
                winCount = 0
            else:
                for var in ret:
                    winCount=var.winCount
            result = yield from conn.execute(sql,[accountId, timeHelp.getNow() - timeRange * 86400])
            if result.rowcount <= 0:
                return {"total":0,"waterCoin":0,"winCoin":0,"winCount":0}
            else:
                for var_row in result:
                    #print(repr(var_row))
                    """
                    mysql> select count(dj_bet.guessUId) as total ,sum(dj_bet.betCoin) as waterCoin,sum(dj_bet.winCoin) as winCoin,count(dj_bet.resultId != '') as winCount from dj_bet where dj_bet.accountId = 'tiger888' and (dj_bet.time between now() and date_sub(now(),interval -1 day)) order by dj_bet.time;
                    +-------+-----------+---------+----------+
                    | total | waterCoin | winCoin | winCount |
                    +-------+-----------+---------+----------+
                    |     1 |        10 |       0 |        1 |
                    +-------+-----------+---------+----------+
                    """
                    return {"total": var_row.total, "waterCoin": int(0 if var_row.waterCoin is None else var_row.waterCoin), "winCoin": int(0 if var_row.winCoin is None else var_row.winCoin), "winCount": winCount}

    @asyncio.coroutine
    def getPinboHistoryAllWaterWinSum(self, timeRange, accountId):
        with (yield from self.objDbMysqlMgr) as conn:
            sql = "select count(wagerId) as total ,sum(toRisk) as waterCoin,sum(winLoss) as winCoin from dj_pinbo_wagers where loginId = %s and wagerDateFm > %s "
            # print(sql)
            sql_winCount = "select count(wagerId) as winCount from dj_pinbo_wagers where winLoss>0 and loginId=%s and wagerDateFm > %s "
            sql_water = "select sum(toRisk) as waterCoin,count(wagerId) as settleCount from dj_pinbo_wagers where loginId = %s and wagerDateFm > %s and status='SETTLED' "
            rest = yield from conn.execute(sql_water,['probet.'+accountId,timeHelp.getNow() - timeRange*86400])
            if rest.rowcount<=0:
                water = 0
                settleCount = 0
            else:
                for x in rest:
                    water=x.waterCoin
                    settleCount = x.settleCount
            ret = yield from conn.execute(sql_winCount,['probet.'+accountId,timeHelp.getNow() - timeRange*86400])
            if ret.rowcount<=0:
                winCount = 0
            else:
                for var in ret:
                    winCount=var.winCount
            result = yield from conn.execute(sql,["probet."+accountId, timeHelp.getNow() - timeRange * 86400])
            if result.rowcount <= 0:
                return {"total":0,"waterCoin":0,"winCoin":0,"winCount":0,"settleCount":0}
            else:
                for var_row in result:
                    #print(repr(var_row))
                    """
                    mysql> select count(dj_bet.guessUId) as total ,sum(dj_bet.betCoin) as waterCoin,sum(dj_bet.winCoin) as winCoin,count(dj_bet.resultId != '') as winCount from dj_bet where dj_bet.accountId = 'tiger888' and (dj_bet.time between now() and date_sub(now(),interval -1 day)) order by dj_bet.time;
                    +-------+-----------+---------+----------+
                    | total | waterCoin | winCoin | winCount |
                    +-------+-----------+---------+----------+
                    |     1 |        10 |       0 |        1 |
                    +-------+-----------+---------+----------+
                    """
                    return {"total": var_row.total, "waterCoin": int(0 if x.waterCoin is None else water), "winCoin": int(0 if var_row.winCoin is None else var_row.winCoin), "winCount": winCount, "settleCount": settleCount}


    @asyncio.coroutine
    def getBetHistoryDetail(self,timeRange,accountId,pageNum,pageSize):
        with (yield from self.objDbMysqlMgr) as conn:
            sql = "select dj_bet.guessUId from dj_bet where dj_bet.accountId = %s and dj_bet.time > %s order by dj_bet.time desc limit %s offset %s"
            #print(sql)
            result = yield from conn.execute(sql,[accountId, timeHelp.getNow() - timeRange * 86400,pageSize, (pageNum-1)*pageSize])
            if result.rowcount <= 0:
                return []
            else:
                retList = []
                for var_row in result:
                    #print(repr(var_row))
                    retList.append(var_row.guessUId)

                return retList

    @asyncio.coroutine
    def getPinBoBetHistoryDetail(self, timeRange, accountId, pageNum, pageSize):
        with (yield from self.objDbMysqlMgr) as conn:
            sql = 'select * from dj_pinbo_wagers where loginId = %s and wagerDateFm > %s order by wagerDateFm desc limit %s offset %s'
            # print(sql)
            result = yield from conn.execute(sql, ["probet."+accountId, timeHelp.getNow() - timeRange * 86400,
                                                   pageSize, (pageNum - 1) * pageSize])
            if result.rowcount <= 0:
                return []
            else:
                retList = []
                for var_row in result:
                    # print(repr(var_row))
                    retList.append(var_row)

                return retList


    @asyncio.coroutine
    def getCoinHistory(self,timeRange,orderType,accountId,pageNum,pageSize):
        with (yield from self.objDbMysqlMgr) as conn:

            beginTime = time.time()

            sql = "select orderId from dj_coin_history where accountId = %s and orderTime > %s and tradeType = %s order by orderTime desc limit %s offset %s"
            result = yield from conn.execute(sql,[accountId, timeRange,orderType,pageSize, (pageNum-1)*pageSize])

            logging.info("execute getCoinHistory sql time[{}]".format(time.time() - beginTime))

            if result.rowcount <= 0:
                return []
            else:
                retList = []
                for var_row in result:
                    retList.append(var_row.orderId)

                return retList

    @asyncio.coroutine
    def appGetCoinHistory(self,orderType,accountId,pageNum,pageSize):
        with (yield from self.objDbMysqlMgr) as conn:

            beginTime = time.time()

            sql = "select dj_coin_history.orderId from dj_coin_history where dj_coin_history.accountId = %s and dj_coin_history.tradeType =%s order by dj_coin_history.orderTime desc limit %s offset %s"
            result = yield from conn.execute(sql,[accountId, orderType,pageSize, (pageNum-1)*pageSize])

            logging.info("execute appGetCoinHistory sql time[{}]".format(time.time() - beginTime))

            if result.rowcount <= 0:
                return []
            else:
                retList = []
                for var_row in result:
                    retList.append(var_row.orderId)
                return retList

    @asyncio.coroutine
    def appGetCoinHisCount(self, orderType, accountId):
        with (yield from self.objDbMysqlMgr) as conn:

            beginTime = time.time()

            sql = "select count(dj_coin_history.orderId) from dj_coin_history where dj_coin_history.accountId = %s and dj_coin_history.tradeType =%s"
            result = yield from conn.execute(sql,[accountId, orderType])

            logging.info("execute appGetCoinHisCount sql time[{}]".format(time.time() - beginTime))

            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    count = var_row[0]
                return count

    @asyncio.coroutine
    def getMsg(self, msgType, pageNum, pageSize):
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            if msgType == 1:
                sql = "select msgId,msgTime,msgTitle,broadcast,msgDetail,sendFrom from dj_all_msg where dj_all_msg.type =%s order by dj_all_msg.msgTime desc limit %s offset %s"
            elif msgType == 2:
                sql = "select msgId,msgTime,msgTitle,sendFrom from dj_all_msg where dj_all_msg.type =%s order by msgTime desc limit %s offset %s"
            result = yield from conn.execute(sql,[msgType,  pageSize, (pageNum - 1) *pageSize])

            sql_count = "select count(dj_all_msg.msgId) from dj_all_msg where dj_all_msg.type=%s"
            ret = yield from conn.execute(sql_count,[msgType])
            logging.info("execute getMsg sql time[{}]".format(time.time() - beginTime))
            if ret.rowcount <= 0:
                return [], 0
            else:
                for var_row in ret:
                    count = var_row[0]
                retList = []
                if msgType == 1:
                    for var_row in result:
                        retdict ={}
                        retdict['msgId'] = var_row.msgId
                        retdict['msgTime'] = var_row.msgTime
                        retdict['msgTitle'] = var_row.msgTitle
                        retdict['broadCast'] = var_row.broadcast
                        retdict['msgDetail'] = var_row.msgDetail
                        retdict['sendFrom'] = var_row.sendFrom
                        retList.append(retdict)
                elif msgType == 2:
                    for var_row in result:
                        retdict ={}
                        retdict['msgId'] = var_row.msgId
                        retdict['msgTime'] = var_row.msgTime
                        retdict['msgTitle'] = var_row.msgTitle
                        retdict['sendFrom'] = var_row.sendFrom
                        retList.append(retdict)

                return retList, count

    @asyncio.coroutine
    def getSysMsg(self, accountId, pageNum, pageSize):
        with (yield from self.objDbMysqlMgr) as conn:

            beginTime = time.time()

            sql = "select msgId,msgTime,msgTitle,readFlag from dj_all_msg where sendTo = %s and isdelete=0 and dj_all_msg.type=0 order by msgTime desc limit %s offset %s"
            result = yield from conn.execute(sql,[accountId,  pageSize, (pageNum - 1) *pageSize])
            logging.info("execute getSysMsg sql time[{}]".format(time.time() - beginTime))

            sql_count = "select count(msgId) from dj_all_msg where sendTo=%s and isdelete=0 and dj_all_msg.type=0"
            ret = yield from conn.execute(sql_count,[accountId])
            logging.info("execute getSysMsgCount sql time[{}]".format(time.time() - beginTime))
            if ret.rowcount <= 0:
                return [], 0
            else:
                for var_row in ret:
                    count = var_row[0]
                retList = []
                for var_row in result:
                    retdict = {}
                    retdict['msgId'] = var_row.msgId
                    retdict['msgTime'] = var_row.msgTime
                    retdict['msgTitle'] = var_row.msgTitle
                    retdict['readFlag'] = var_row.readFlag
                    retList.append(retdict)
                return retList, count

    @asyncio.coroutine
    def getAgentMsg(self, agentId, pageNum, pageSize):
        with (yield from self.objDbMysqlMgr) as conn:

            beginTime = time.time()

            sql = "select msgId,msgTime,msgTitle,readFlag from dj_all_msg where sendTo = %s and isdelete=0 and dj_all_msg.type=3 order by msgTime desc limit %s offset %s"
            result = yield from conn.execute(sql,[agentId,  pageSize, (pageNum - 1) *pageSize])

            sql_count = "select count(msgId) from dj_all_msg where sendTo=%s and isdelete=0 and dj_all_msg.type=3"
            ret = yield from conn.execute(sql_count,[agentId])
            logging.info("execute getAgentMsg sql time[{}]".format(time.time() - beginTime))
            if ret.rowcount <= 0:
                return [], 0
            else:
                for var_row in ret:
                    count = var_row[0]
                retList = []
                for var_row in result:
                    retdict = {}
                    retdict['msgId'] = var_row.msgId
                    retdict['msgTime'] = var_row.msgTime
                    retdict['msgTitle'] = var_row.msgTitle
                    retdict['readFlag'] = var_row.readFlag
                    retList.append(retdict)
                return retList, count

    @asyncio.coroutine
    def appGetAgentMsg(self, agentId):
        with (yield from self.objDbMysqlMgr) as conn:

            beginTime = time.time()

            sql = "select msgId,msgTime,msgTitle,readFlag from dj_all_msg where sendTo = %s and isdelete=0 and dj_all_msg.type=3 order by msgTime desc limit %s,%s"
            result = yield from conn.execute(sql, [agentId, 0, 6])

            logging.info("execute appGetAgentMsg sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return []
            else:
                retList = []
                for var_row in result:
                    retdict = {}
                    retdict['msgId'] = var_row.msgId
                    retdict['msgTime'] = var_row.msgTime
                    retdict['msgTitle'] = var_row.msgTitle
                    retdict['readFlag'] = var_row.readFlag
                    retList.append(retdict)
                return retList

    @asyncio.coroutine
    def getAgentMsgUnReadNum(self, agentId):
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select count(msgId) from dj_all_msg where sendTo = %s and readFlag = 0 and isdelete=0 and dj_all_msg.type=3"
            result = yield from conn.execute(sql,[agentId])
            logging.info("execute getAgentMsgUnReadNum sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row[0]:
                        unReadNum = var_row[0]
                    else:
                        unReadNum = 0
                return unReadNum

    @asyncio.coroutine
    def changeReadFlag(self, msgId):
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "update dj_all_msg set readFlag = 1 where dj_all_msg.msgId = %s"
            yield from conn.execute(sql,[msgId])

            logging.info("execute changeReadFlag sql time[{}]".format(time.time() - beginTime))

    @asyncio.coroutine
    def getSysMsgUnReadNum(self, accountId):
        with (yield from self.objDbMysqlMgr) as conn:

            beginTime = time.time()

            sql = "select count(msgId) from dj_all_msg where sendTo = %s and readFlag = 0 and isdelete=0"
            result = yield from conn.execute(sql,[accountId])

            logging.info("execute getSysMsgUnReadNum sql time[{}]".format(time.time() - beginTime))

            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row[0]:
                        unReadNum = var_row[0]
                    else:
                        unReadNum = 0
                return unReadNum

    @asyncio.coroutine
    def delMsg(self, msgId):
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "delete from dj_all_msg where dj_all_msg.msgId = %s "
            yield from conn.execute(sql,[msgId])
            logging.info("execute delMsg sql time[{}]".format(time.time() - beginTime))

    @asyncio.coroutine
    def delUserMsg(self, msgId):
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "update dj_all_msg set isdelete=1 where msgId = %s "
            yield from conn.execute(sql,[msgId])
            logging.info("execute delMsg sql time[{}]".format(time.time() - beginTime))

    @asyncio.coroutine
    def getRepairData(self, pageNum:int):
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql_0 = "select repairId,start_time,end_time from dj_repair where dj_repair.repairFlag=0 order by create_time desc limit %s offset %s"
            result = yield from conn.execute(sql_0,10, (pageNum-1)*10)
            logging.info("execute getRepairedData sql time[{}]".format(time.time() - beginTime))
            sql_1 = "select repairId,start_time,end_time,repairFlag from dj_repair where dj_repair.repairFlag=1"
            ret = yield from conn.execute(sql_1)
            if result.rowcount <= 0:
                repairedDataList = []
            else:
                repairedDataList = []
                for var_row in result:
                    repairedDataDict = {}
                    repairedDataDict['strRepairId'] = var_row.repairId
                    repairedDataDict['iStartTime'] = var_row.start_time
                    repairedDataDict['iEndTime'] = var_row.end_time
                    repairedDataDict['iTimeOfUse'] = var_row.end_time - var_row.start_time
                    repairedDataList.append(repairedDataDict)
            if ret.rowcount <= 0:
                repairingDataList = []
            else:
                repairingDataList = []
                for var_row in ret:
                    repairingDataDict = {}
                    repairingDataDict['strRepairId'] = var_row.repairId
                    repairingDataDict['iStartTime'] = var_row.start_time
                    repairingDataDict['iEndTime'] = var_row.end_time
                    repairingDataDict['iRepairFlag'] = var_row.repairFlag
                    repairingDataList.append(repairingDataDict)

            return repairedDataList, repairingDataList

            
    @asyncio.coroutine
    def getRepairedCount(self):
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select count(dj_repair.repairId) from dj_repair where dj_repair.repairFlag=0"
            result = yield from conn.execute(sql)

            logging.info("execute getRepairedCount sql time[{}]".format(time.time() - beginTime))

            if result.rowcount <= 0:
                return 0
            else:
                count = 0
                for var_row in result:
                    count = var_row[0]
                return count

    @asyncio.coroutine
    def getAccountPinboHistoryValidWater(self, timeBegin, timeEnd, accountId):
        from thirdweb.handle.pinbo.wagerschanges import getPinboHistoryValidWater

        with (yield from self.objDbMysqlMgr) as conn:
            sql_eu, sql_am = getPinboHistoryValidWater()
            result = yield from conn.execute(sql_eu, [accountId, timeBegin, timeEnd])
            ret = yield from conn.execute(sql_am, [accountId, timeBegin, timeEnd])
            if result.rowcount <= 0:
                validWaterCoinEu = 0
            else:
                for var_row in result:
                    if var_row.validWaterCoin is None:
                        # 如果没有统计符合条件的，这个None就是0
                        validWaterCoinEu = 0
                    else:
                        validWaterCoinEu = int(var_row.validWaterCoin)
            if ret.rowcount <= 0:
                validWaterCoinAm = 0
            else:
                for var in ret:
                    if var.validWaterCoin is None:
                        # 如果没有统计符合条件的，这个None就是0
                        validWaterCoinAm = 0
                    else:
                        validWaterCoinAm = int(var.validWaterCoin)
            return validWaterCoinEu + validWaterCoinAm

    @asyncio.coroutine
    def getAllPinboHistoryValidWater(self, timeBegin, timeEnd):
        from thirdweb.handle.pinbo.wagerschanges import getAllPinboHistoryValidWater

        with (yield from self.objDbMysqlMgr) as conn:
            sql_eu, sql_am = getAllPinboHistoryValidWater()
            result = yield from conn.execute(sql_eu,[timeBegin, timeEnd])
            ret = yield from conn.execute(sql_am,[timeBegin, timeEnd])
            retList = []
            if result.rowcount <= 0:
                pass
            else:
                for var_row in result:
                    if not var_row[0]:
                        continue
                    else:
                        retList.append({"loginId":var_row.loginId,"validWaterCoin": var_row.validWaterCoin})
            if ret.rowcount <= 0:
                pass
            else:
                for var in ret:
                    if not var[0]:
                        continue
                    else:
                        retList.append({"loginId":var.loginId,"validWaterCoin": var.validWaterCoin})
            return retList

    @asyncio.coroutine
    def getOnePinboHistoryValidWater(self, accountId, timeBegin, timeEnd):
        from thirdweb.handle.pinbo.wagerschanges import getOnePinboHistoryValidWater
        with (yield from self.objDbMysqlMgr) as conn:
            sql_eu, sql_am = getOnePinboHistoryValidWater()
            result = yield from conn.execute(sql_eu,[accountId,timeBegin, timeEnd])
            ret = yield from conn.execute(sql_am,[accountId,timeBegin, timeEnd])
            if result.rowcount <= 0:
                validWaterCoinEu = 0
            else:
                for var_row in result:
                    if var_row.validWaterCoin is None:
                        validWaterCoinEu = 0
                    else:
                        validWaterCoinEu = int(var_row.validWaterCoin)
            if ret.rowcount <= 0:
                validWaterCoinAm = 0
            else:
                for var in ret:
                    if var.validWaterCoin is None:
                        validWaterCoinAm = 0
                    else:
                        validWaterCoinAm = int(var.validWaterCoin)
            return validWaterCoinEu+validWaterCoinAm

    @asyncio.coroutine
    def getAccountFirstPayByDay(self, accountId):
        """每月首充24内的存款"""
        with (yield from self.objDbMysqlMgr) as conn:
            sql = "select orderTime from dj_coin_history where accountId=%s and tradeType=1 and tradeState=1 and orderTime between %s and %s"
            result = yield from conn.execute(sql,[accountId, timeHelp.monthStartTimestamp(), timeHelp.nextMonthStartTimestamp()])
            if result.rowcount <= 0:
                return 0,0
            else:
                var_row = yield from result.fetchone()
                firstOrderTime = var_row[0]
                sql = "select sum(coinNum) from dj_coin_history where accountId=%s and tradeType=1 and tradeState=1 and orderTime between %s and %s"
                ret = yield from conn.execute(sql,[accountId, firstOrderTime, (firstOrderTime+86400)])
                var = yield from ret.fetchone()
                deposit = var[0]
                return deposit,firstOrderTime

    @asyncio.coroutine
    def getValidWaterMonthly(self, accountId):
        """当月有效流水"""
        with (yield from self.objDbMysqlMgr) as conn:
            sql = "select sum(validWater) from dj_coin_history where accountId=%s and tradeState=1 and orderTime between %s and %s"
            result = yield from conn.execute(sql,[accountId, timeHelp.monthStartTimestamp(), timeHelp.nextMonthStartTimestamp()])
            if result.rowcount <= 0:
                return 0
            else:
                var_row = yield from result.fetchone()
                if var_row[0] is None:
                    return 0
                else:
                    validWaterMonthly = var_row[0]
                    return int(validWaterMonthly)

    @asyncio.coroutine
    def getValidWaterByTimeRange(self, beginTime,endTime,accountId):
        """当月有效流水"""
        with (yield from self.objDbMysqlMgr) as conn:
            sql = "select sum(validWater) from dj_coin_history where accountId=%s and tradeState=1 and orderTime between %s and %s"
            result = yield from conn.execute(sql, [accountId, beginTime,endTime])
            if result.rowcount <= 0:
                return 0
            else:
                var_row = yield from result.fetchone()
                if var_row[0] is None:
                    return 0
                else:
                    validWaterMonthly = var_row[0]
                    return validWaterMonthly


    # 代理相关
    @asyncio.coroutine
    def getAgentConfig(self):
        """获取代理配置"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select * from dj_agent_config"
            result = yield from conn.execute(sql)
            logging.info("execute getAgentConfig sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return {}
            else:
                agentConfig = {}
                for var_row in result:
                    agentConfig['pingboRate'] = var_row.pingboRate
                    agentConfig['probetRate'] = var_row.probetRate
                    agentConfig['qqRate'] = var_row.qqRate
                    agentConfig['alipayRate'] = var_row.alipayRate
                    agentConfig['unionpayRate'] = var_row.unionpayRate
                    agentConfig['bankTransferRate'] = var_row.bankTransferRate
                    agentConfig['alipayTransferRate'] = var_row.alipayTransferRate
                    agentConfig['weixinTransferRate'] = var_row.weixinTransferRate
                    agentConfig['drawingRate'] = var_row.drawingRate
                    agentConfig['Lv1'] = var_row.Lv1
                    agentConfig['Lv2'] = var_row.Lv2
                    agentConfig['Lv3'] = var_row.Lv3
                    agentConfig['Lv4'] = var_row.Lv4
                    agentConfig['Lv5'] = var_row.Lv5
                return agentConfig

    @asyncio.coroutine
    def getAgentData(self, agentId, pn=1):
        """获取代理id"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            if agentId:
                sql_count = "select count(agentId) from dj_agent where agentId=%s"
                sql = "select agentId from dj_agent where agentId=%s "
            else:
                sql_count = "select count(agentId) from dj_agent"
                sql = "select agentId from dj_agent limit %s, %s"
            ret = yield from conn.execute(sql_count,[agentId] if agentId else [])
            result = yield from conn.execute(sql,[agentId] if agentId else [(pn-1)*10, pn*10])
            logging.info("execute getAgentData sql time[{}]".format(time.time() - beginTime))
            if ret.rowcount <= 0:
                count = 0
            else:
                for var in ret:
                    count = var[0]
            if result.rowcount <= 0:
                return []
            else:
                agentList = []
                for var_row in result:
                    agentList.append(var_row.agentId)
                return agentList, count

    @asyncio.coroutine
    def getAccountByAgent(self, agentId):
        """获取下线用户Id"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select accountId from dj_account where agentId=%s "
            result = yield from conn.execute(sql,[agentId])
            logging.info("execute getAccountByAgent sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return []
            else:
                accountIds = []
                for var in result:
                    accountIds.append(var[0])
                return accountIds

    @asyncio.coroutine
    def getAccountCountByAgent(self, agentId):
        """获取下线总用户"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select count(accountId) from dj_account where agentId=%s "
            result = yield from conn.execute(sql,[agentId])
            logging.info("execute getAccountCountByAgent sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    count = var_row[0]
                return count

    @asyncio.coroutine
    def getActivelyAccount(self, agentId, start_time, end_time):
        """获取活跃用户"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select count(accountId) from dj_account where agentId=%s and loginTime between %s and %s"
            result = yield from conn.execute(sql,[agentId, start_time, end_time])
            logging.info("execute getActivelyAccount sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    count = var_row[0]
                return count

    @asyncio.coroutine
    def getAccountAllDeposit(self, agentId, start_time, end_time):
        """获取下线用户总存款"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) from dj_coin_history where tradeType=1 and tradestate=1 and accountId in (select accountId from dj_account where agentId=%s) and orderTime between %s and %s"
            result = yield from conn.execute(sql,[agentId, start_time, end_time])
            logging.info("execute getAccountAllDeposit sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row[0]:
                        allDeposit = var_row[0]
                    else:
                        allDeposit = 0
                return allDeposit

    @asyncio.coroutine
    def getAccountAllDrawing(self, agentId, start_time, end_time):
        """获取下线用户总提款"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) from dj_coin_history where tradeType=2 and tradestate=1 and accountId in (select accountId from dj_account where agentId=%s) and orderTime between %s and %s"
            result = yield from conn.execute(sql,[agentId, start_time, end_time])
            logging.info("execute getAccountAllDrawing sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row[0]:
                        allDrawing = var_row[0]
                    else:
                        allDrawing = 0
                return allDrawing

    @asyncio.coroutine
    def getAccountPinboBackWater(self, agentId, start_time, end_time):
        """获取下线用户平博总反水"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) from dj_coin_history where tradeType=7 and accountId in (select accountId from dj_account where agentId=%s) and orderTime between %s and %s"
            result = yield from conn.execute(sql,[agentId, start_time, end_time])
            logging.info("execute getAccountPinboBackWater sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row[0]:
                        pingboBackWater = var_row[0]
                    else:
                        pingboBackWater = 0
                return pingboBackWater

    @asyncio.coroutine
    def getAccountProbetBackWater(self, agentId, start_time, end_time):
        """获取下线用户电竞总反水"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) from dj_coin_history where tradeType=8 and accountId in (select accountId from dj_account where agentId=%s) and orderTime between %s and %s"
            result = yield from conn.execute(sql,[agentId, start_time, end_time])
            logging.info("execute getAccountProbetBackWater sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row[0]:
                        probetBackWater = var_row[0]
                    else:
                        probetBackWater = 0
                return probetBackWater

    @asyncio.coroutine
    def getAccountActivetyBonus(self, agentId, start_time, end_time):
        """获取下线用户活动总奖金"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) as coin from dj_coin_history where tradeType=9 and accountId in (select accountId from dj_account where agentId=%s) and orderTime between %s and %s"
            result = yield from conn.execute(sql,[agentId, start_time, end_time])
            logging.info("execute getAccountActivetyBonus sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.coin:
                        activetyBonus = var_row.coin
                    else:
                        activetyBonus = 0
                return activetyBonus

    @asyncio.coroutine
    def getAccountAllCoin(self, agentId, start_time, end_time):
        """获取下线活跃用户总余额"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coin+guessCoin+pingboCoin) as coin from dj_account where agentId=%s and loginTime between %s and %s"

            result = yield from conn.execute(sql,[agentId, start_time, end_time])
            logging.info("execute getAccountAllCoin sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.coin:
                        allBalance = var_row.coin
                    else:
                        allBalance = 0
                return allBalance

    @asyncio.coroutine
    def getAccountPingboAllWinLoss(self, agentId, start_time, end_time):
        """获取下线平博总输赢"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            accoutIds = yield from classSqlBaseMgr.getInstance().getAccountByAgent(agentId)
            ids = ["probet." + x for x in accoutIds]
            if len(ids)==0:
                return 0
            sql = "select sum(winLoss) as winLoss from dj_pinbo_wagers where loginId in (%s) and status='SETTLED' "%",".join(["%s"]*len(ids))
            sql=sql+" and wagerDateFm between %s and %s"
            ids.extend([start_time, end_time])
            result = yield from conn.execute(sql,ids)
            logging.info("execute getAccountPingboWinLoss sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.winLoss:
                        allWinLoss = var_row.winLoss
                    else:
                        allWinLoss = 0
                return allWinLoss

    @asyncio.coroutine
    def getAccountPingboWater(self, agentId, start_time, end_time):
        """获取下线平博流水"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            accoutIds = yield from classSqlBaseMgr.getInstance().getAccountByAgent(agentId)
            ids = ["probet." + x for x in accoutIds]
            if len(ids) == 0:
                return 0
            sql = "select sum(toRisk) as waterCoin from dj_pinbo_wagers where loginId in (%s) and status='SETTLED' "%",".join(["%s"]*len(ids))
            sql=sql+"and wagerDateFm between %s and %s"
            ids.extend([start_time, end_time])
            result = yield from conn.execute(sql,ids)
            logging.info("execute getAccountPingboWater sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.waterCoin:
                        waterCoin = var_row.waterCoin
                    else:
                        waterCoin = 0
                return waterCoin

    @asyncio.coroutine
    def getAccountPingboWaterBack(self, agentId, start_time, end_time):
        """获取下线平博反水"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()

            sql = "select sum(coinNum) as coin from dj_coin_history where accountId in (select accountId from dj_account where agentId=%s) and tradeType=7 and orderTime between %s and %s"
            result = yield from conn.execute(sql,[agentId, start_time, end_time])
            logging.info("execute getAccountPingboWaterBack sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.coin:
                        backCoin = var_row.coin
                    else:
                        backCoin = 0
                return backCoin

    @asyncio.coroutine
    def getAccountProbetAllWinCoin(self, agentId, start_time, end_time):
        """获取下线电竞总输赢"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(winCoin-betCoin) as winLoss from dj_bet where accountId in (select accountId from dj_account where agentId=%s) and result != '' and dj_bet.time between %s and %s"
            result = yield from conn.execute(sql,[agentId, start_time, end_time])
            logging.info("execute getAccountProbetWinCoin sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.winLoss:
                        allWinLoss = var_row.winLoss
                    else:
                        allWinLoss = 0
                return allWinLoss

    @asyncio.coroutine
    def getAccountProbetWater(self, agentId, start_time, end_time):
        """获取下线电竞流水"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(betCoin) as waterCoin from dj_bet where accountId in (select accountId from dj_account where agentId=%s) and result != '' and dj_bet.time between %s and %s"
            result = yield from conn.execute(sql,[agentId, start_time, end_time])
            logging.info("execute getAccountProbetWater sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.waterCoin:
                        waterCoin = var_row.waterCoin
                    else:
                        waterCoin = 0
                return waterCoin

    @asyncio.coroutine
    def getAccountProbetWaterBack(self, agentId, start_time, end_time):
        """获取下线电竞反水"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()

            sql = "select sum(coinNum) as coin from dj_coin_history where accountId in (select accountId from dj_account where agentId=%s) and tradeType=8 and orderTime between %s and %s"
            result = yield from conn.execute(sql,[agentId, start_time, end_time])
            logging.info("execute getAccountProbetWaterBack sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.coin:
                        backCoin = var_row.coin
                    else:
                        backCoin = 0
                return backCoin

    @asyncio.coroutine
    def getAccountDataByAgent(self, agentId, start_time, end_time, pn=1):
        """获取下线用户"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql_count = "select count(accountId) from dj_account where agentId=%s and loginTime between %s and %s"
            sql = "select accountId,regTime,loginTime from dj_account where agentId=%s and loginTime between %s and %s order by loginTime desc limit %s offset %s"
            ret = yield from conn.execute(sql_count,[agentId, start_time, end_time])
            result = yield from conn.execute(sql,[agentId, start_time, end_time, 10, (pn-1)*10])
            logging.info("execute getAccountDataByAgent sql time[{}]".format(time.time() - beginTime))
            accountList = []
            if ret.rowcount <= 0:
                return accountList, 0
            else:
                for var in ret:
                    count = var[0]
                for var_row in result:
                    accountDict = {}
                    accountDict['accountId'] = var_row.accountId
                    accountDict['regTime'] = var_row.regTime
                    accountDict['loginTime'] = var_row.loginTime
                    accountList.append(accountDict)
                return accountList, count

    @asyncio.coroutine
    def getNewAccountCount(self, agentId, start_time, end_time):
        """获取每月下线新用户数量"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select count(accountId) as countNum from dj_account where agentId=%s and regTime between %s and %s"
            result = yield from conn.execute(sql,[agentId, start_time, end_time])
            logging.info("execute getNewAccountCount sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    count = var_row.countNum
                return count


    @asyncio.coroutine
    def getAccountAllBalance(self, accountId):
        """获取用户总余额"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql_coin = "select sum(coin+guessCoin+pingboCoin) from dj_account where accountId=%s"
            result = yield from conn.execute(sql_coin,[accountId])

            logging.info("execute getAccountAllBalance sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                coin = 0
            else:
                for var_row in result:
                    if var_row[0]:
                        coin = var_row[0]
                    else:
                        coin = 0
            return coin

    @asyncio.coroutine
    def getAccountDeposit(self, accountId, start_time, end_time):
        """获取用户总存款"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) from dj_coin_history where accountId=%s and tradeType=1 and tradestate=1 and orderTime between %s and %s"
            result = yield from conn.execute(sql,[accountId, start_time, end_time])
            logging.info("execute getAccountDeposit sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row[0]:
                        deposit = var_row[0]
                    else:
                        deposit = 0
                return deposit

    @asyncio.coroutine
    def getAccountDrawing(self, accountId, start_time, end_time):
        """获取用户总提现"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) from dj_coin_history where accountId=%s and tradeType=2 and tradestate=1 and orderTime between %s and %s"
            result = yield from conn.execute(sql,[accountId, start_time, end_time])
            logging.info("execute getAccountDrawing sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row[0]:
                        drawing = var_row[0]
                    else:
                        drawing = 0
                return drawing

    @asyncio.coroutine
    def getAccountPingboWinLoss(self, accountId, start_time, end_time):
        """获取用户平博输赢"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            accountId = "probet." + accountId
            sql = "select sum(winLoss) as winLoss from dj_pinbo_wagers where loginId=%s and status='SETTLED' "
            sql = sql + " and wagerDateFm between %s and %s"
            params = [accountId,start_time,end_time]
            result = yield from conn.execute(sql, params)
            logging.info("execute getAccountPingboWinLoss sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.winLoss:
                        allWinLoss = var_row.winLoss
                    else:
                        allWinLoss = 0
                return allWinLoss

    @asyncio.coroutine
    def getAccountProbetWinCoin(self, accountId, start_time, end_time):
        """获取用户电竞输赢"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(winCoin-betCoin) as winLoss from dj_bet where accountId=%s and result != '' and dj_bet.time between %s and %s"
            result = yield from conn.execute(sql, [accountId, start_time, end_time])
            logging.info("execute getAccountProbetWinCoin sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.winLoss:
                        allWinLoss = var_row.winLoss
                    else:
                        allWinLoss = 0
                return allWinLoss

    @asyncio.coroutine
    def getAccountDividend(self, accountId, start_time, end_time):
        """获取用户反水和红利"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) from dj_coin_history where accountId=%s and (tradeType=7 or tradeType=8 or tradeType=9) and orderTime between %s and %s"
            result = yield from conn.execute(sql,[accountId,start_time, end_time])
            logging.info("execute getAccountDividend sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row[0]:
                        dividend = var_row[0]
                    else:
                        dividend = 0
                return dividend

    @asyncio.coroutine
    def getAllBankInfo(self):
        """获取收款银行卡信息"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select dj_offline_account_recharge.name,accountId,bank,bankInfo from dj_offline_account_recharge where status=0 and kind=1"
            result = yield from conn.execute(sql)
            logging.info("execute getAllBankInfo sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return []
            else:
                accountInfoList = []
                for var_row in result:
                    accountInfo = {}
                    accountInfo['name'] = var_row.name
                    accountInfo['bank'] = var_row.bank
                    accountInfo['bankInfo'] = var_row.bankInfo
                    accountInfo['accountId'] = var_row.accountId
                    accountInfoList.append(accountInfo)
                return accountInfoList

    @asyncio.coroutine
    def getAllAlipayInfo(self):
        """获取收款支付宝信息"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select dj_offline_account_recharge.name,accountId from dj_offline_account_recharge where status=0 and kind=0"
            result = yield from conn.execute(sql)
            logging.info("execute getAllAlipayInfo sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return []
            else:
                accountInfoList = []
                for var_row in result:
                    accountInfo = {}
                    accountInfo['name'] = var_row.name
                    accountInfo['accountId'] = var_row.accountId
                    accountInfoList.append(accountInfo)
                return accountInfoList

    @asyncio.coroutine
    def getAllWeixinInfo(self):
        """获取收款微信信息"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select dj_offline_account_recharge.name,accountId from dj_offline_account_recharge where status=0 and kind=2"
            result = yield from conn.execute(sql)
            logging.info("execute getAllWeixinInfo sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return []
            else:
                accountInfoList = []
                for var_row in result:
                    accountInfo = {}
                    accountInfo['name'] = var_row.name
                    accountInfo['accountId'] = var_row.accountId
                    accountInfoList.append(accountInfo)
                return accountInfoList

    @asyncio.coroutine
    def getBankTransfer(self,agentId, start_time, end_time):
        """获取下线总银行卡存款"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) as coinNum from dj_coin_history where tradeType=1 and tradestate=1 and transFrom='银行卡转账' and accountId in (select accountId from dj_account where agentId=%s) and orderTime between %s and %s"
            result = yield from conn.execute(sql,[agentId, start_time, end_time])
            logging.info("execute getBankTransfer sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.coinNum:
                        allDeposit = var_row.coinNum
                    else:
                        allDeposit = 0
                return allDeposit

    @asyncio.coroutine
    def getUnionpay(self, agentId, start_time, end_time):
        """获取下线总银联扫码存款"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) as coinNum from dj_coin_history where tradeType=1 and tradestate=1 and transFrom='银联扫码' and accountId in (select accountId from dj_account where agentId=%s) and orderTime between %s and %s"
            result = yield from conn.execute(sql,[agentId, start_time, end_time])
            logging.info("execute getUnionpay sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.coinNum:
                        allDeposit = var_row.coinNum
                    else:
                        allDeposit = 0
                return allDeposit

    @asyncio.coroutine
    def getQQpay(self, agentId, start_time, end_time):
        """获取下线总QQ扫码支付存款"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) as coinNum from dj_coin_history where tradeType=1 and tradestate=1 and transFrom='QQ扫码' and accountId in (select accountId from dj_account where agentId=%s) and orderTime between %s and %s"
            result = yield from conn.execute(sql,[agentId, start_time, end_time])
            logging.info("execute getQQpay sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.coinNum:
                        allDeposit = var_row.coinNum
                    else:
                        allDeposit = 0
                return allDeposit

    @asyncio.coroutine
    def getAlipay(self, agentId, start_time, end_time):
        """获取下线总支付宝扫码存款"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) as coinNum from dj_coin_history where tradeType=1 and tradestate=1 and transFrom='支付宝扫码' and accountId in (select accountId from dj_account where agentId=%s) and orderTime between %s and %s"
            result = yield from conn.execute(sql,[agentId, start_time, end_time])
            logging.info("execute getAlipay sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.coinNum:
                        allDeposit = var_row.coinNum
                    else:
                        allDeposit = 0
                return allDeposit

    @asyncio.coroutine
    def getAlipayTransfer(self, agentId, start_time, end_time):
        """获取下线总支付宝转账存款"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) as coinNum from dj_coin_history where tradeType=1 and tradestate=1 and transFrom='支付宝转账' and accountId in (select accountId from dj_account where agentId=%s) and orderTime between %s and %s"
            result = yield from conn.execute(sql,[agentId, start_time, end_time])
            logging.info("execute getAlipayTransfer sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.coinNum:
                        allDeposit = var_row.coinNum
                    else:
                        allDeposit = 0
                return allDeposit

    @asyncio.coroutine
    def getWeixinPay(self, agentId, start_time, end_time):
        """获取下线总微信转账存款"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) as coinNum from dj_coin_history where tradeType=1 and tradestate=1 and transFrom='微信扫码' and accountId in (select accountId from dj_account where agentId=%s) and orderTime between %s and %s"
            result = yield from conn.execute(sql, [agentId, start_time, end_time])
            logging.info("execute getWeixinPay sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.coinNum:
                        allDeposit = var_row.coinNum
                    else:
                        allDeposit = 0
                return allDeposit

    @asyncio.coroutine
    def getWeixinTransfer(self, agentId, start_time, end_time):
        """获取下线总微信转账存款"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) as coinNum from dj_coin_history where tradeType=1 and tradestate=1 and transFrom='微信转账' and accountId in (select accountId from dj_account where agentId=%s) and orderTime between %s and %s"
            result = yield from conn.execute(sql,[agentId, start_time, end_time])
            logging.info("execute getWeixinTransfer sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.coinNum:
                        allDeposit = var_row.coinNum
                    else:
                        allDeposit = 0
                return allDeposit

    @asyncio.coroutine
    def getAccountBankTransfer(self, accountId, start_time, end_time):
        """获取用户银行卡存款"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) as coinNum from dj_coin_history where tradeType=1 and tradestate=1 and transFrom='银行卡转账' and accountId=%s and orderTime between %s and %s"
            result = yield from conn.execute(sql,[accountId, start_time, end_time])
            logging.info("execute getAccountBankTransfer sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.coinNum:
                        allDeposit = var_row.coinNum
                    else:
                        allDeposit = 0
                return allDeposit

    @asyncio.coroutine
    def getAccountUnionpay(self, accountId, start_time, end_time):
        """获取用户银联扫码存款"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) as coinNum from dj_coin_history where tradeType=1 and tradestate=1 and transFrom='银联扫码' and accountId=%s and orderTime between %s and %s"
            result = yield from conn.execute(sql,[accountId, start_time, end_time])
            logging.info("execute getAccountUnionpay sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.coinNum:
                        allDeposit = var_row.coinNum
                    else:
                        allDeposit = 0
                return allDeposit

    @asyncio.coroutine
    def getAccountQQpay(self, accountId, start_time, end_time):
        """获取用户QQ扫码支付存款"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) as coinNum from dj_coin_history where tradeType=1 and tradestate=1 and transFrom='QQ扫码' and accountId=%s and orderTime between %s and %s"
            result = yield from conn.execute(sql,[accountId, start_time, end_time])
            logging.info("execute getAccountQQpay sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.coinNum:
                        allDeposit = var_row.coinNum
                    else:
                        allDeposit = 0
                return allDeposit

    @asyncio.coroutine
    def getAccountAlipay(self, accountId, start_time, end_time):
        """获取用户支付宝扫码存款"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) as coinNum from dj_coin_history where tradeType=1 and tradestate=1 and transFrom='支付宝扫码' and accountId=%s and orderTime between %s and %s"
            result = yield from conn.execute(sql,[accountId, start_time, end_time])
            logging.info("execute getAccountAlipay sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.coinNum:
                        allDeposit = var_row.coinNum
                    else:
                        allDeposit = 0
                return allDeposit

    @asyncio.coroutine
    def getAccountAlipayTransfer(self, accountId, start_time, end_time):
        """获取用户支付宝转账存款"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) as coinNum from dj_coin_history where tradeType=1 and tradestate=1 and transFrom='支付宝转账' and accountId=%s and orderTime between %s and %s"
            result = yield from conn.execute(sql,[accountId, start_time, end_time])
            logging.info("execute getAccountAlipayTransfer sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.coinNum:
                        allDeposit = var_row.coinNum
                    else:
                        allDeposit = 0
                return allDeposit

    @asyncio.coroutine
    def getAccountWeixinPay(self, accountId, start_time, end_time):
        """获取用户微信转账存款"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) as coinNum from dj_coin_history where tradeType=1 and tradestate=1 and transFrom='微信扫码' and accountId=%s and orderTime between %s and %s"
            result = yield from conn.execute(sql, [accountId, start_time, end_time])
            logging.info("execute getAccountWeixinPay sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.coinNum:
                        allDeposit = var_row.coinNum
                    else:
                        allDeposit = 0
                return allDeposit

    @asyncio.coroutine
    def getAccountWeixinTransfer(self, accountId, start_time, end_time):
        """获取用户微信转账存款"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime = time.time()
            sql = "select sum(coinNum) as coinNum from dj_coin_history where tradeType=1 and tradestate=1 and transFrom='微信转账' and accountId=%s and orderTime between %s and %s"
            result = yield from conn.execute(sql,[accountId, start_time, end_time])
            logging.info("execute getAccountWeixinTransfer sql time[{}]".format(time.time() - beginTime))
            if result.rowcount <= 0:
                return 0
            else:
                for var_row in result:
                    if var_row.coinNum:
                        allDeposit = var_row.coinNum
                    else:
                        allDeposit = 0
                return allDeposit

    @asyncio.coroutine
    def getFirstRechCoin(self,strAccountId,iActiveTime):
        #获取首冲后24小时的总充值额
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime=time.time()
            sql="select sum(coinNum) from dj_coin_history WHERE accountId=%s and sradeState=1  AND orderTime BETWEEN %s AND %s"
            result=yield from conn.execute(sql,[strAccountId,iActiveTime,iActiveTime+86400])
            logging.info("execute getFirstRechValidWater sql time[{}]".format(time.time() - beginTime))
            if result.rowcount<=0:
                return 0
            else:
                result = yield from result.fetchone()
                return 0 if result[0] is None else int(result[0])

    @asyncio.coroutine
    def getAgentCommissionCount(self,agentId,start_time=0, end_time=0):
        """获取代理佣金报表数据的数量"""
        with (yield from self.objDbMysqlMgr) as conn:
            beginTime=time.time()
            if not all([start_time,end_time]):
                sql = "select count(billId) as countNum from dj_agent_commission where agentId=%s"
                params = [agentId]
            else:
                startYear = timeHelp.getYear(start_time)
                startMonth = timeHelp.getMonth(start_time)
                endYear = timeHelp.getYear(end_time)
                endMonth = timeHelp.getMonth(end_time)
                sql = "select count(billId) as countNum from dj_agent_commission where agentId=%s and (dateYear between %s and %s) and (dateMonth between %s and %s)"
                params = [agentId,startYear,endYear,startMonth,endMonth]
            result = yield from conn.execute(sql,params)
            logging.info("execute getAgentCommissionCount sql time[{}]".format(time.time() - beginTime))
            if result.rowcount<=0:
                return 0
            else:
                result = yield from result.fetchone()
                return 0 if result[0] is None else int(result[0])
