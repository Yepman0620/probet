from lib.redismodule.redisMgr import classAioRedis
import aioredis
import asyncio
import uuid
import os
import hashlib
import glob
import random
from logic.data.matchData import classMatchData, classGuessData
from logic.data.userData import classUserData, classUserBetHistory, classUserCoinHistory, classRepairData, \
    classMessageData, classAgentData, classAgentCommissionData,classConfig
from config.zoneConfig import userConfig, matchConfig, miscConfig
import logging
import threading
from datawrapper.redisOperateKey import *
from error.errorCode import errorLogic, exceptionLogic
from lib import constants
import pickle
import json
from lib.jsonhelp import jsonSerialiser


class classDataBaseMgr():
    _instance = {}
    _instance_lock = threading.Lock()
    _defaultInstance = "default"

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            # if not hasattr(cls, "_instance") or "__instanceName__" in kwargs:
            if "__instanceName__" in kwargs:
                objInstance = cls.getInstance(kwargs["__instanceName__"])
            else:
                objInstance = cls.getInstance(cls._defaultInstance)

            if objInstance is None:
                objNew = object.__new__(cls)
                objNew.__init__(*args, **kwargs)
                # 拥有多个单例对象
                if "__instanceName__" in kwargs:
                    cls._instance[kwargs["__instanceName__"]] = objNew
                else:
                    cls._instance[cls._defaultInstance] = objNew

        return cls._instance

    @classmethod
    def getInstance(cls, instanceName=None):
        if instanceName is None:
            return cls._instance.get(cls._defaultInstance, None)
        else:
            return cls._instance.get(instanceName, None)

    def __init__(self, redisConfig, aioLoop, debugFlag=True, minPoolSize: int = 5, maxPoolSize: int = 5):

        self.dictAioRedis = {}

        for var_key, var_config in redisConfig.items():

            if var_config['hashRing'] != 0:
                if not isinstance(var_config['address'], list):
                    raise RuntimeError("redis config error")

            self.dictAioRedis[var_key] = classAioRedis(var_config['address'],
                                                       var_config['pwd'], var_config['dbIndex'],
                                                       aioLoop, minPoolSize, maxPoolSize)
        self.dictScriptNameSha = {}
        self.bDebug = debugFlag

    def __del__(self):
        pass

    def dumps(self, debugFlag: bool, obj, **args):
        # 调试的时候用json
        if debugFlag:
            return jsonSerialiser.dumps(obj, **args)
        else:
            return pickle.dumps(obj, **args)

    def loads(self, debugFlag: bool, obj, **args):
        # 调试的时候用json
        if debugFlag:
            return jsonSerialiser.loads(obj.decode(), **args)
        else:
            return pickle.loads(obj, **args)

    @asyncio.coroutine
    def connectRedis(self):
        print("test")
        for var_key, var_aio_obj in self.dictAioRedis.items():
            yield from var_aio_obj.connectRedis()
            # TODO log

    @asyncio.coroutine
    def loadRedisLuaScript(self):

        try:

            for var_key, var_aio_obj in self.dictAioRedis.items():
                if var_aio_obj.bHashRing:
                    listAllNodesRedisPool = var_aio_obj.getAllRedisPool()
                    for var_pool in listAllNodesRedisPool:
                        with (yield from var_pool) as redis:
                            # yield from self.objAioRedis.script_flush()
                            temp_list = glob.glob(os.path.dirname(os.path.realpath(__file__)) + "/../redisscript/*.lua")
                            for filename in temp_list:

                                temp_script_file = open(filename, "r")
                                if temp_script_file is not None:
                                    temp_script_content = temp_script_file.read()

                                    temp_sha = yield from redis.script_load(temp_script_content)
                                    purefilename = filename[filename.rfind('/') + 1:]

                                    self.dictScriptNameSha[purefilename] = temp_sha
                                    print(purefilename)
                                    # logging.getLogger('logic').info("load lua script [{}] sha[{}]".format(purefilename, temp_sha))
                else:
                    with (yield from var_aio_obj.getRedisPool()) as redis:

                        temp_list = glob.glob(os.path.dirname(os.path.realpath(__file__)) + "/../redisscript/*.lua")
                        for filename in temp_list:

                            temp_script_file = open(filename, "r")
                            if temp_script_file is not None:
                                temp_script_content = temp_script_file.read()

                                temp_sha = yield from redis.script_load(temp_script_content)
                                purefilename = filename[filename.rfind('/') + 1:]
                                self.dictScriptNameSha[purefilename] = temp_sha
                                print(purefilename)
                                # logging.getLogger('logic').info("load lua script [{}] sha[{}]".format(purefilename, temp_sha))
        except Exception as e:
            logging.error("init redis failed")
            exit(0)

    @asyncio.coroutine
    def preLoadRedisLuaScript(self):

        temp_list = glob.glob(os.path.dirname(os.path.realpath(__file__)) + "/../../redisscript/*.lua")
        for filename in temp_list:

            temp_script_file = open(filename, "r")
            if temp_script_file is not None:
                temp_script_content = temp_script_file.read()
                # temp_sha = yield from redis.script_load(temp_script_content)

                purefilename = filename[filename.rfind('/') + 1:]
                objSha = hashlib.sha1(temp_script_content)
                temp_sha = objSha.hexdigest()
                self.dictScriptNameSha[purefilename] = temp_sha
                logging.info("load lua script [{}] sha[{}]".format(purefilename, temp_sha))

    @asyncio.coroutine
    def getPlayerDataByLock(self, accountId: str, reenTrantLock: str = None):
        if reenTrantLock is None:
            strLockId = str(uuid.uuid1())
        else:
            # 重入锁
            strLockId = reenTrantLock

        iTryCount = 5
        while iTryCount > 0:
            try:
                with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:

                    iTryCount -= 1
                    objPlayerBytes = yield from redis.evalsha(self.dictScriptNameSha['getPlayerDataByLock.lua'],
                                                              [playerDataHash,
                                                               playerLockIdKey.format(accountId),
                                                               playerLockTimeKey.format(accountId)],
                                                              [accountId, "True", strLockId, 500])

                    if objPlayerBytes is not None:
                        return self.loads(self.bDebug, objPlayerBytes), strLockId
                    else:
                        return None, ""
            except aioredis.errors.ReplyError as e:
                if e.args[0].find("locked"):
                    logging.error("playerData accountId[{}] is lock".format(accountId))
                    if iTryCount <= 0:
                        raise exceptionLogic(errorLogic.data_locked)
                    yield from asyncio.sleep(random.uniform(0, 0.3))
                    continue

    @asyncio.coroutine
    def setPlayerDataByLock(self, playerData: classUserData, lock: str = "", save=True, new=False):
        bytesPlayerData = self.dumps(self.bDebug, playerData)
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from redis.evalsha(self.dictScriptNameSha['setPlayerDataByLock.lua'],
                                     [playerDataHash,
                                      playerDataKeyDirtyList,
                                      playerDataKeyNewList,
                                      playerLockIdKey.format(playerData.strAccountId),
                                      playerLockTimeKey.format(playerData.strAccountId)],
                                     [playerData.strAccountId, bytesPlayerData, lock, str(save), str(new)])

    @asyncio.coroutine
    def releasePlayerDataLock(self, accountId: str, lock: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            # TODO 用lua 来修改用户数据
            yield from redis.delete(playerLockIdKey.format(accountId))

    @asyncio.coroutine
    def getPlayerData(self, accountId: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            # TODO 用lua 来修改用户数据
            bytesPlayerData = yield from redis.hget(playerDataHash, accountId)
            if bytesPlayerData is None:
                return None
            else:
                return self.loads(self.bDebug, bytesPlayerData)

    @asyncio.coroutine
    def checkPlayerExists(self, accountId: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            # TODO 用lua 来修改用户数据
            ret = yield from redis.hexists(playerDataHash, accountId)
            if int(ret) == 1:
                return True
            else:
                return False

    @asyncio.coroutine
    def increasePlayerCoin(self, accountId: str, coin: int):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            iRet = yield from redis.hincrby(playerCoinHash, accountId, coin)
            return int(iRet)

    @asyncio.coroutine
    def getPlayerCoin(self, accountId: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            iRet = yield from redis.hget(playerCoinHash, accountId)
            return int(iRet)

    ###比赛相关的
    @asyncio.coroutine
    def getMatchDataByLock(self, matchId: str, reenTrantLock: str = None):

        if reenTrantLock is None:
            strLockId = str(uuid.uuid1())
        else:
            # 重入锁
            strLockId = reenTrantLock
        iTryCount = 5
        while iTryCount > 0:
            try:

                with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:

                    objMatchBytes = yield from redis.evalsha(self.dictScriptNameSha['getMatchDataByLock.lua'],
                                                             [matchDataHash,
                                                              matchLockIdKey.format(matchId),
                                                              matchLockTimeKey.format(matchId)],
                                                             [matchId, "True", strLockId, 500])

                    if objMatchBytes is not None:
                        return self.loads(self.bDebug, objMatchBytes), strLockId

            except aioredis.errors.ReplyError as e:
                if e.args[0].find("locked"):
                    logging.error("matchData matchId[{}] is lock".format(matchId))
                    if iTryCount <= 0:
                        raise exceptionLogic(errorLogic.data_locked)
                    yield from asyncio.sleep(random.uniform(0, 0.3))
                    continue

    @asyncio.coroutine
    def getMatchData(self, matchId: str):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            bytesMatchData = yield from redis.hget(matchDataHash, matchId)
            if bytesMatchData is None:
                return None
            else:
                return self.loads(self.bDebug, bytesMatchData)

    @asyncio.coroutine
    def setMatchDataByLock(self, matchData: classMatchData, lock: str = ""):
        bytesMatchData = self.dumps(self.bDebug, matchData)

        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            yield from redis.evalsha(self.dictScriptNameSha['setMatchDataByLock.lua'],
                                     [matchDataHash,
                                      matchLockIdKey.format(matchData.strMatchId),
                                      matchLockTimeKey.format(matchData.strMatchId),
                                      matchDataKeyDirtyList],
                                     [matchData.strMatchId, bytesMatchData, lock])

    @asyncio.coroutine
    def releaseMatchDataLock(self, matchId: str, lock: str):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            # TODO 用lua 来修改比赛数据
            yield from redis.delete(matchLockIdKey.format(matchId))

    @asyncio.coroutine
    def delMatchData(self, matchId: str):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            yield from redis.hdel(matchDataHash, matchId)

    @asyncio.coroutine
    def getMatchDataList(self, matchIdList: list):
        if len(matchIdList) <= 0:
            return []

        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:

            listMatchData = yield from redis.evalsha(self.dictScriptNameSha['getMatchListData.lua'],
                                                     [matchDataHash],
                                                     matchIdList)
            if listMatchData is None:
                return []

            listRet = []
            for var_MatchData in listMatchData:
                if var_MatchData is None:
                    continue
                listRet.append(self.loads(self.bDebug, var_MatchData))

            return listRet

    @asyncio.coroutine
    def getMatchDataListRetDict(self, matchIdList: list):

        if len(matchIdList) <= 0:
            return {}

        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:

            listMatchData = yield from redis.evalsha(self.dictScriptNameSha['getMatchListData.lua'],
                                                     [matchDataHash],
                                                     matchIdList)
            dictRet = {}
            for var_MatchData in listMatchData:
                if var_MatchData is None:
                    continue
                objMatchData = self.loads(self.bDebug, var_MatchData)
                dictRet[objMatchData.strMatchId] = objMatchData

            return dictRet

    # 竞猜相关
    @asyncio.coroutine
    def getGuessDataByLock(self, guessId: str, reenTrantLock: str = None):

        if reenTrantLock is None:
            strLockId = str(uuid.uuid1())
        else:
            # 重入锁
            strLockId = reenTrantLock
        iTryCount = 5
        while iTryCount > 0:
            try:

                with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:

                    objMatchBytes = yield from redis.evalsha(self.dictScriptNameSha['getGuessData.lua'],
                                                             [guessDataHash,
                                                              guessLockIdKey.format(guessId),
                                                              guessLockTimeKey.format(guessId)],
                                                             [guessId, "True", strLockId, 500])

                    if objMatchBytes is not None:
                        return self.loads(self.bDebug, objMatchBytes), strLockId
                    else:
                        return None, ""
            except aioredis.errors.ReplyError as e:
                if e.args[0].find("locked"):
                    logging.error("guessData guessId[{}] is lock".format(guessId))
                    if iTryCount <= 0:
                        raise exceptionLogic(errorLogic.data_locked)
                    yield from asyncio.sleep(random.uniform(0, 0.3))
                    continue

    @asyncio.coroutine
    def getGuessData(self, guessId):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            bytesGuessData = yield from redis.hget(guessDataHash, guessId)
            if bytesGuessData is None:
                return None
            else:
                return self.loads(self.bDebug, bytesGuessData)

    @asyncio.coroutine
    def setGuessDataByLock(self, guessData: classGuessData, lock: str = ""):
        bytesGuessData = self.dumps(self.bDebug, guessData)
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            yield from redis.evalsha(self.dictScriptNameSha['setGuessDataByLock.lua'],
                                     [guessDataHash,
                                      guessLockIdKey.format(guessData.strGuessId),
                                      guessLockTimeKey.format(guessData.strGuessId),
                                      guessDataKeyDirtyList],
                                     [guessData.strGuessId, bytesGuessData, lock])

    @asyncio.coroutine
    def releaseGuessLock(self, guess_id: str, lock: str = ""):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            yield from redis.delete(guessLockIdKey.format(guess_id))

    @asyncio.coroutine
    def addGuessData(self, guessData: classGuessData):
        bytesGuessData = self.dumps(self.bDebug, guessData)
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            yield from redis.hset(guessDataHash, guessData.strGuessId, bytesGuessData)


            yield from redis.hset(guessDataHash,guessData.strGuessId,bytesGuessData)
            yield from redis.sadd(guessDataKeyNewList,guessData.strGuessId)

    @asyncio.coroutine
    def delGuessData(self, guessId: str):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            yield from redis.hdel(guessDataHash, guessId)

    # 判断比赛是否已经存在了
    @asyncio.coroutine
    def checkPreMatchIdExist(self, match_id: str, match_type: str):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            redisMatchApprovalSortKey = "preMatchDataForApprovalSortKey"
            redisMatchSortKey = "matchDataSortListKey_{}".format(match_type)

            ret = yield from redis.zscore(redisMatchApprovalSortKey, match_id)
            if ret is None:
                ret = yield from redis.zscore(redisMatchSortKey, match_id)
                if ret is None:
                    return False

            return True

    @asyncio.coroutine
    def addPreMatchForApproval(self, matchData: classMatchData):

        bytesMatchObjData = self.dumps(self.bDebug, matchData)

        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            redisMatchApprovalSortKey = "preMatchDataForApprovalSortKey"

            objPipline = redis.pipeline()

            objPipline.zadd(redisMatchApprovalSortKey, matchData.iMatchStartTimestamp, matchData.strMatchId)
            objPipline.hset(matchDataHash, matchData.strMatchId, bytesMatchObjData)
            yield from objPipline.execute()

    @asyncio.coroutine
    def agreeApprovalData(self, matchData: classMatchData):

        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            redisMatchApprovalSortKey = "preMatchDataForApprovalSortKey"

            # TODO lua script
            objPipline = redis.pipeline()

            objPipline.zrem(redisMatchApprovalSortKey, matchData.strMatchId)

            # 比赛排序
            objPipline.zadd("matchDataSortListKey_all", matchData.iMatchStartTimestamp,
                            matchData.strMatchId)
            # 分类下放一个,以后改到不同数据库里面去
            objPipline.zadd("matchDataSortListKey_{}".format(matchData.strMatchType), matchData.iMatchStartTimestamp,
                            matchData.strMatchId)

            # 分类下放一个
            objPipline.zadd("matchDataSortListKey_doing".format(matchData.strMatchType), matchData.iMatchStartTimestamp,
                            matchData.strMatchId)

            objPipline.sadd(matchDataKeyNewList, matchData.strMatchId)

            yield from objPipline.execute()

    @asyncio.coroutine
    def setMatchDataBeginTime(self, match_obj: classMatchData):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            objPipline = redis.pipeline()
            objPipline.zadd("matchDataSortListKey_{}".format(match_obj.strMatchType), match_obj.iMatchStartTimestamp,
                            match_obj.strMatchId)
            objPipline.zadd("matchDataSortListKey_all".format(match_obj.strMatchType), match_obj.iMatchStartTimestamp,
                            match_obj.strMatchId)

            yield from objPipline.execute()

    @asyncio.coroutine
    def getMatchAwardedList(self, beginPos, endPos):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            listIds = yield from redis.zrange("matchAwardedSortList", beginPos, endPos)
            iCount = yield from redis.zcount("matchAwardedSortList")
            return listIds, iCount

    @asyncio.coroutine
    def changeTwoSetList(self, spopkey, saddkey):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            popId = yield from redis.evalsha(self.dictScriptNameSha['getGuessTeamAwardChange.lua'],
                                             [spopkey,
                                              saddkey])
            return popId


    @asyncio.coroutine
    def addMatchAwardedList(self, match_id, time):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            yield from redis.zadd("matchAwardedSortList", time, match_id)

    @asyncio.coroutine
    def getMatchAwardedList(self, beginPos, endPos):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            listIds = yield from redis.zrange("matchAwardedSortList", beginPos, endPos)
            iCount = yield from redis.zcount("matchAwardedSortList")
            return listIds, iCount

    @asyncio.coroutine
    def delMatchAwardedList(self, match_id):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            yield from redis.zrem("matchAwardedSortList", match_id)

    @asyncio.coroutine
    def addMatchCancelAwardedList(self, match_id, time):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            yield from redis.zadd("matchCancelAwardSortList", time, match_id)

    @asyncio.coroutine
    def getMatchCancelAwardedList(self, beginPos, endPos):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            listIds = yield from redis.zrange("matchCancelAwardSortList", beginPos, endPos)
            iCount = yield from redis.zcount("matchCancelAwardSortList")
            return listIds, iCount

    @asyncio.coroutine
    def delMatchCancelAwardedList(self, match_id):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            yield from redis.zrem("matchCancelAwardSortList", match_id)

    @asyncio.coroutine
    def setMatchResultFinish(self, match_id: str, match_type, time: int):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            objPipline = redis.pipeline()
            objPipline.zadd("matchDataSortListKey_finish", time, match_id)
            objPipline.zrem("matchDataSortListKey_doing", match_id)
            objPipline.zrem("matchDataSortListKey_{}".format(match_type), match_id)
            yield from objPipline.execute()

    @asyncio.coroutine
    def getMatchResultDoing(self, beginIndex, endIndex):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            listDoingIds = yield from redis.zrange("matchDataSortListKey_doing", beginIndex, endIndex)
            return listDoingIds

    @asyncio.coroutine
    def getFinishResultMatch(self, beginIndex, endIndex):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            listFinishIds = yield from redis.zrange("matchDataSortListKey_finish", beginIndex, endIndex)
            return listFinishIds

    @asyncio.coroutine
    def getRecentMatchFinishDataCount(self):

        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            iCount = yield from redis.zcount("matchDataSortListKey_finish")
            return iCount

    @asyncio.coroutine
    def getRecentMatchDoingDataCount(self):

        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            iCount = yield from redis.zcount("matchDataSortListKey_doing")
            return iCount

    """
    @asyncio.coroutine
    def addMatchWinPlayerId(self, account_id):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            objPipline = redis.pipeline()
            objPipline.sadd("matchWinUniqueAward", account_id)
            objPipline.sadd("matchAllUniqueAward", account_id)
            yield from objPipline.execute()

    @asyncio.coroutine
    def addMatchLostPlayerId(self, account_id):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            objPipline = redis.pipeline()
            objPipline.sadd("matchLoseUniqueAward", account_id)
            objPipline.sadd("matchAllUniqueAward", account_id)
            yield from objPipline.execute()
    """

    @asyncio.coroutine
    def getPreMatchDataListRetDict(self):
        redisMatchApprovalSortKey = "preMatchDataForApprovalSortKey"

        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            listPreMatchIds = yield from redis.zrevrange(redisMatchApprovalSortKey, 0, -1)
            if listPreMatchIds is None:
                return {}
            else:

                listMatchBytesData = yield from redis.hmget(matchDataHash, "", *listPreMatchIds)
                if listMatchBytesData is None:
                    return {}
                retDict = {}
                for var in listMatchBytesData:
                    if var is None:
                        continue
                    objMatchData = self.loads(self.bDebug, var)

                    retDict[objMatchData.strMatchId] = objMatchData

                return retDict

    @asyncio.coroutine
    def getPreMatchDataList(self, beginPos: int, endPos: int, matchType: str = ""):

        redisMatchApprovalSortKey = "preMatchDataForApprovalSortKey"
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            listPreMatchIds = yield from redis.zrevrange(redisMatchApprovalSortKey, beginPos, endPos)
            if len(listPreMatchIds) <= 0:
                return []
            else:

                listMatchBytesData = yield from redis.hmget(matchDataHash, *listPreMatchIds)
                if len(listMatchBytesData) <= 0:
                    return []
                retList = []

                for var in listMatchBytesData:
                    if var is None:
                        continue
                    objMatchData = self.loads(self.bDebug, var)
                    retList.append(objMatchData)

                return retList

    @asyncio.coroutine
    def getMatchDataListByScore(self, beginScore: int, endScore: int, listType: str = ""):

        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:

            listMatchIds = yield from redis.zrevrange("matchDataSortListKey_{}".format(listType), beginScore, endScore)
            if len(listMatchIds) <= 0:
                return []
            listMatchBytes = yield from redis.hmget(matchDataHash, *listMatchIds)

            listRet = []
            for var_matchDataBytes in listMatchBytes:
                if var_matchDataBytes is None:
                    continue
                listRet.append(self.loads(self.bDebug, var_matchDataBytes))

            return listRet

    @asyncio.coroutine
    def getMatchDataListByRange(self, beginPos: int, endPos: int, listType: str = ""):

        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:

            listMatchIds = yield from redis.zrevrange("matchDataSortListKey_{}".format(listType), beginPos, endPos)
            if len(listMatchIds) <= 0:
                return []
            listMatchBytes = yield from redis.hmget(matchDataHash, *listMatchIds)

            listRet = []
            for var_matchDataBytes in listMatchBytes:
                if var_matchDataBytes is None:
                    continue
                listRet.append(self.loads(self.bDebug, var_matchDataBytes))

            return listRet

    @asyncio.coroutine
    def getRecentMatchDataListByPage(self, pageNum, pageCount=10, type=""):

        iBeginIndex = pageNum * pageCount
        iEndIndex = iBeginIndex + pageCount

        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:

            listMatchData = yield from redis.evalsha(self.dictScriptNameSha['getRecentMatchListDataByPage.lua'],
                                                     ["matchDataSortListKey_{}".format(type), "matchDataKey"],
                                                     [iBeginIndex, iEndIndex])
            listRet = []
            for var_matchData in listMatchData:
                if var_matchData is None:
                    continue
                listRet.append(self.loads(self.bDebug, var_matchData))

            return listRet

    @asyncio.coroutine
    def getGuessDataListRetDict(self, guessIdList: list):

        if len(guessIdList) <= 0:
            return {}

        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:

            listGuessDataBytes = yield from redis.hmget(guessDataHash, "", *guessIdList)
            dictRet = {}
            for var_guessData in listGuessDataBytes:
                if var_guessData is None:
                    continue
                objGuessData = self.loads(self.bDebug, var_guessData)
                dictRet[objGuessData.strGuessId] = objGuessData

            return dictRet

    @asyncio.coroutine
    def resetResultRedisList(self, guessId: str, dict_key: str):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            yield from redis.set("resultRedisListPos_{}_{}".format(guessId, dict_key), 0)

    @asyncio.coroutine
    def resetResultRedisListByScore(self, matchId: str, dictKey: str):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            yield from redis.set("resultRedisListPos_{}_{}".format(matchId, dictKey), 0)

    @asyncio.coroutine
    def resetResultRedisListByScore(self, matchId: str, teamKey: str, resetTime):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            yield from redis.incrby("resultRedisListScore_{}_{}".format(matchId, teamKey), resetTime)

    # 运营用的
    @asyncio.coroutine
    def getGuessMemberStaticListByScore(self, guess_id, start_score, end_score):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            # 反着查
            listResp = yield from redis.zrevrangebyscore("recentBetPlayer_{}".format(guess_id), start_score, end_score)

            listRet = []
            if listResp is None or len(listResp) <= 0:
                return listRet

            for var_resp in listResp:
                if var_resp is not None:
                    listRet.append(json.loads(var_resp))

            return listRet

    @asyncio.coroutine
    def getGraphBetRange(self, guess_id: str, team_id: str, range_list: list):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            objPipline = redis.pipeline()
            for var_range in range_list:
                objPipline.hget("graphBetRange_{}_{}".format(guess_id, team_id), str(var_range))

            listResult = yield from objPipline.execute()
            listRet = []
            for var_ret in listResult:
                if var_ret is None:
                    listRet.append(0)
                else:
                    listRet.append(int(var_ret))
            return listRet

    @asyncio.coroutine
    def getCurrentGuessMemberLen(self, guess_id: str):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            iLen = yield from redis.zcount("recentBetPlayer_{}".format(guess_id))
            return iLen

    @asyncio.coroutine
    def getCurrentGuessMember(self, guess_id: str, begin_index, end_index):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            listRecentBytes = yield from redis.zrange("recentBetPlayer_{}".format(guess_id), begin_index, end_index)
            listRet = []
            for var in listRecentBytes:
                listRet.append(json.loads(var))
            return listRet

    # *************************************

    @asyncio.coroutine
    def removeNew(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem(playerDataKeyNewList, remove_item)

    @asyncio.coroutine
    def getAccountDataDirtyList(self, redisPool):
        with (yield from redisPool) as redis:
            listDirtyId = yield from redis.smembers(playerDataKeyDirtyList)
            return listDirtyId

    @asyncio.coroutine
    def removeDirty(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem(playerDataKeyDirtyList, remove_item)

    @asyncio.coroutine
    def getAccountDataNewList(self, redisPool):
        with (yield from redisPool) as redis:
            listNewId = yield from redis.smembers(playerDataKeyNewList)
            return listNewId

    @asyncio.coroutine
    def getMatchDataNewList(self, redisPool):
        with (yield from redisPool) as redis:
            listNewMatchId = yield from redis.smembers(matchDataKeyNewList)
            return listNewMatchId

    @asyncio.coroutine
    def removeMatchNew(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem(matchDataKeyNewList, remove_item)

    @asyncio.coroutine
    def getMatchDataDirtyList(self, redisPool):
        with (yield from redisPool) as redis:
            listMatchDirtyId = yield from redis.smembers(matchDataKeyDirtyList)
            return listMatchDirtyId

    @asyncio.coroutine
    def removeMatchDirty(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem(matchDataKeyDirtyList, remove_item)

    # 获取新竞猜玩法数据
    @asyncio.coroutine
    def getMatchGuessDataNewList(self, redisPool):
        with (yield from redisPool) as redis:
            listNewMatchGuessIds = yield from redis.smembers(guessDataKeyNewList)
            return listNewMatchGuessIds

    # 删除新竞猜玩法数据
    @asyncio.coroutine
    def removeMatchGuessNew(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem(guessDataKeyNewList, remove_item)

    # 获取竞猜玩法数据
    @asyncio.coroutine
    def getMatchGuessDataDirtyList(self, redisPool):
        with (yield from redisPool) as redis:
            listMatchGuessDirtyId = yield from redis.smembers(guessDataKeyDirtyList)
            return listMatchGuessDirtyId

    # 删除竞猜玩法数据
    @asyncio.coroutine
    def removeMatchGuessDirty(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem(guessDataKeyDirtyList, remove_item)

    # 获取用户新下注数据
    @asyncio.coroutine
    def getPlayerBetDataNewList(self, redisPool):
        with (yield from redisPool) as redis:
            listNewPlayerBetIds = yield from redis.smembers("playerBetHistoryHashKey_new")
            return listNewPlayerBetIds

    # 删除用户新下注数据
    @asyncio.coroutine
    def removePlayerBetNew(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem("playerBetHistoryHashKey_new", remove_item)

    # 获取用户下注数据
    @asyncio.coroutine
    def getPlayerBetDataDirtyList(self, redisPool):
        with (yield from redisPool) as redis:
            listDirtyPlayerBetIds = yield from redis.smembers("playerBetHistoryHashKey_dirty")
            return listDirtyPlayerBetIds

    # 删除用户下注数据
    @asyncio.coroutine
    def removePlayerBetDirty(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem("playerBetHistoryHashKey_dirty", remove_item)

    # 获取新产生的用户金币增加、消耗数据
    @asyncio.coroutine
    def getPlayerCoinHistoryOrderDataNewList(self, redisPool):
        with (yield from redisPool) as redis:
            listNewPlayerOrderIds = yield from redis.smembers("playerCoinHistoryKey_New")
            return listNewPlayerOrderIds

    # 删除用户新充值订单数据
    @asyncio.coroutine
    def removePlayerCoinHistoryOrderNew(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem("playerCoinHistoryKey_New", remove_item)

    # 获取新产生的用户金币增加、消耗数据
    @asyncio.coroutine
    def getPlayerCoinHistoryOrderDataDirtyList(self, redisPool):
        with (yield from redisPool) as redis:
            listNewPlayerOrderIds = yield from redis.smembers("playerCoinHistoryKey_Dirty")
            return listNewPlayerOrderIds

    # 删除用户新充值订单数据
    @asyncio.coroutine
    def removePlayerCoinHistoryOrderDirty(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem("playerCoinHistoryKey_Dirty", remove_item)

    @asyncio.coroutine
    def getCoinHis(self, order_id, redisPool):
        with (yield from redisPool) as redis:
            ret = yield from redis.hget("playerCoinHistoryHashKey", order_id)
            if ret is None:
                return None
            else:
                return self.loads(self.bDebug, ret)

    @asyncio.coroutine
    def getCoinHisByLock(self, order_id):
        # TODO
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            ret = yield from redis.hget("playerCoinHistoryHashKey", order_id)
            if ret is None:
                return None
            else:
                return self.loads(self.bDebug, ret)

    @asyncio.coroutine
    def getCoinHisList(self, order_id_list: list):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            listDataBytes = yield from redis.hmget("playerCoinHistoryHashKey", "", *order_id_list)
            if listDataBytes is None:
                return []
            else:
                retList = []
                for var in listDataBytes:
                    if var is None:
                        continue
                    retList.append(self.loads(self.bDebug, var))
                return retList

    @asyncio.coroutine
    def getAccountGuessBet(self, account_id: str, guess_id: str):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            bytesAlreadyBet = yield from redis.hget("uniqueAccount_{}".format(guess_id), account_id)
            if bytesAlreadyBet is None:
                return 0
            else:

                if len(bytesAlreadyBet) <= 0:
                    return 0
                else:
                    return int(bytesAlreadyBet)

    @asyncio.coroutine
    def getBetData(self, account_id: str, match_id: str, guess_id: str):

        strGuessLock = str(uuid.uuid1())
        strPlayerLock = str(uuid.uuid1())
        objMatchData = None
        objGuessData = None
        objPlayerData = None

        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:

            ret = yield from redis.evalsha(self.dictScriptNameSha['getBetData.lua'], [
                matchDataHash,
                matchLockIdKey.format(match_id),
                matchLockTimeKey.format(match_id),
                guessDataHash,
                guessLockIdKey.format(guess_id),
                guessLockTimeKey.format(guess_id),
                playerDataHash,
                playerLockIdKey.format(account_id),
                playerLockTimeKey.format(account_id)],
                                           [match_id, guess_id, strGuessLock, 500, account_id, strPlayerLock])

            if ret[0] is not None:
                objMatchData = self.loads(self.bDebug, ret[0])
            if ret[1] is not None:
                objGuessData = self.loads(self.bDebug, ret[1])
            if ret[2] is not None:
                objPlayerData = self.loads(self.bDebug, ret[2])

            return objPlayerData, strPlayerLock, objMatchData, objGuessData, strGuessLock

    @asyncio.coroutine
    def addBetData(self, chooseId: str, guess_obj: classGuessData, player_obj: classUserData,
                   guess_lock: str, player_lock: str, guess_history_obj: classUserBetHistory, add_time: int):

        bytesPlayerData = self.dumps(self.bDebug, player_obj)
        bytesHistoryData = self.dumps(self.bDebug, guess_history_obj)
        bytesGuessData = self.dumps(self.bDebug, guess_obj)

        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            yield from redis.evalsha(self.dictScriptNameSha['saveBetData.lua'],
                                     [playerDataHash,
                                      playerLockIdKey.format(player_obj.strAccountId),
                                      playerLockTimeKey.format(player_obj.strAccountId),
                                      "playerBetHistorySortKey_{}".format(player_obj.strAccountId),
                                      "playerBetHistoryHashKey",
                                      "playerBetHistoryHashKey_new",
                                      "matchGuessMemberKey_{}".format(guess_obj.strGuessId + '_' + str(chooseId)),
                                      guessDataHash,
                                      guessDataKeyDirtyList,
                                      guessLockIdKey.format(guess_obj.strGuessId),
                                      guessLockTimeKey.format(guess_obj.strGuessId)
                                      ],
                                     [bytesGuessData,
                                      guess_obj.strGuessId, guess_lock, guess_history_obj.strGuessUId, add_time,
                                      bytesPlayerData, player_obj.strAccountId, player_lock,
                                      guess_history_obj.strGuessUId,
                                      guess_history_obj.iTime,
                                      bytesHistoryData
                                      ])

    @asyncio.coroutine
    def addPlayerCoinRecord(self, account_id: str, order_data: classUserCoinHistory):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            objPipline = redis.pipeline()
            objPipline.zadd("playerCoinHistorySortKey_{}".format(account_id), order_data.iTime,
                            order_data.strOrderId)
            objPipline.hset("playerCoinHistoryHashKey", order_data.strOrderId,
                            self.dumps(self.bDebug, order_data))

            objPipline.sadd("playerCoinHistoryKey_New", order_data.strOrderId)
            yield from objPipline.execute()

    @asyncio.coroutine
    def setPlayerCoinRecord(self, account_id: str, order_data: classUserCoinHistory):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            objPipline = redis.pipeline()
            objPipline.zadd("playerCoinHistorySortKey_{}".format(account_id), order_data.iTime,
                            order_data.strOrderId)
            objPipline.hset("playerCoinHistoryHashKey", order_data.strOrderId,
                            self.dumps(self.bDebug, order_data))

            objPipline.sadd("playerCoinHistoryKey_Dirty", order_data.strOrderId)
            yield from objPipline.execute()

    @asyncio.coroutine
    def getBetHistoryList(self, bet_history_uid_list: list):

        if len(bet_history_uid_list) <= 0:
            return []

        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            listBetHistoryBytes = yield from redis.hmget("playerBetHistoryHashKey", "", *bet_history_uid_list)
            retList = []
            if listBetHistoryBytes is None:
                return retList
            else:
                for var_bytes in listBetHistoryBytes:
                    if var_bytes is None:
                        # TODO log error
                        continue

                    retList.append(pickle.loads(var_bytes))

                return retList



    @asyncio.coroutine
    def getBetHistory(self, bet_history_uid: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            bytesHistoryData = yield from redis.hget("playerBetHistoryHashKey", bet_history_uid)
            if bytesHistoryData is None:
                return []
            else:
                return self.loads(self.bDebug, bytesHistoryData)

    @asyncio.coroutine
    def setBetHistory(self, betHisData):
        bytesHisData = self.dumps(self.bDebug, betHisData)
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from redis.zadd("playerBetHistorySortKey_{}".format(betHisData.strAccountId), betHisData.iTime,
                                  betHisData.strGuessUId)
            yield from redis.hset("playerBetHistoryHashKey", betHisData.strGuessUId, bytesHisData)
            yield from redis.sadd("playerBetHistoryHashKey_dirty", betHisData.strGuessUId)

    """"
    # 交易记录
    @asyncio.coroutine
    def setUserCoinRecord(self, accountId: str, orderId: str, tradeType: int, orderData: classUserCoinHistory):
        bytesOrderDataData = self.dumps(self.bDebug,orderData)
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from redis.hset("tradeHistory_{}".format(accountId), orderId, bytesOrderDataData)
            yield from redis.zadd("tradeHistorySortSet_{}".format(accountId), orderData.iTime, orderId)
            yield from redis.zadd("{}_HistorySortSet".format(tradeType), orderData.iTime, orderId)


    @asyncio.coroutine
    def getUserCoinRecord(self, accountId: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            orderIdList = yield from redis.zrange("tradeHistorySortSet_{}".format(accountId), 0, -1)
            orderDataList = []
            for var in orderIdList:
                bytesOrderDataData = yield from redis.hget("tradeHistory_{}".format(accountId), var)
                if bytesOrderDataData is None:
                    return None
                else:
                    orderDataList.append(pickle.loads(bytesOrderDataData))
            return orderDataList

    @asyncio.coroutine
    def getTradeTypeRecord(self, accountId: str, tradeType: int, startTime: int, endTime: int):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            orderIdList = yield from redis.zrevrangebyscore("{}_HistorySortSet".format(tradeType), endTime, startTime)
            orderDataList = []
            for var in orderIdList:
                bytesOrderDataData = yield from redis.hget("tradeHistory_{}".format(accountId), var)
                if bytesOrderDataData is None:
                    return None
                else:
                    orderDataList.append(pickle.loads(bytesOrderDataData))
            return orderDataList
    """


    # 代理消息
    @asyncio.coroutine
    def addAgentMsg(self, agentMsgData: classMessageData, msgId:str):
        bytesAgentMsgData = self.dumps(self.bDebug, agentMsgData)
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            if not msgId:
                yield from self.addNewAgentMsgToList(redis, agentMsgData.strMsgId + '_' + agentMsgData.strAccountId)
            else:
                yield from self.addAgentMsgKeyDirtyList(redis, msgId + '_' + agentMsgData.strAccountId)
            yield from redis.zadd("AgentMsg", agentMsgData.iMsgTime,
                                  agentMsgData.strMsgId + '_' + agentMsgData.strAccountId)
            yield from redis.hset("AgentMsgHash", agentMsgData.strMsgId + '_' + agentMsgData.strAccountId,
                                  bytesAgentMsgData)

    # 代理获取消息
    @asyncio.coroutine
    def getOneAgentMsg(self, msgId: str, agentId: str):
        """获取详细信息"""
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            bytesAgentMsgData = yield from redis.hget("AgentMsgHash", msgId + '_' + agentId)
            if bytesAgentMsgData is None:
                return None
            else:
                agentMsgData = self.loads(self.bDebug, bytesAgentMsgData)
                agentMsgData.iReadFlag = 1
                bytesAgentMsgData = self.dumps(self.bDebug, agentMsgData)
                yield from redis.hset("AgentMsgHash", msgId + '_' + agentId, bytesAgentMsgData)
                return agentMsgData

    @asyncio.coroutine
    def delAgentMsg(self, msgId: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from redis.zrem("AgentMsg", msgId)
            yield from redis.hdel("AgentMsgHash", msgId)

    # 代理消息入库
    @asyncio.coroutine
    def addNewAgentMsgToList(self, redisPool, agentMsgId):
        # 新增代理消息到队列
        yield from redisPool.sadd(agentMsgNewKeyList, agentMsgId)

    @asyncio.coroutine
    def getAgentMsgNewList(self, redisPool):
        # 获取代理消息新列表
        with (yield from redisPool) as redis:
            listNewMsg = yield from redis.smembers(agentMsgNewKeyList)
            return listNewMsg

    @asyncio.coroutine
    def removeAgentMsgNew(self, redisPool, remove_item):
        # 删除代理新信息
        with (yield from redisPool) as redis:
            yield from redis.srem(agentMsgNewKeyList, remove_item)

    @asyncio.coroutine
    def addAgentMsgKeyDirtyList(self, redisPool, MsgId):
        yield from redisPool.sadd(agentMsgKeyDirtyList, MsgId)


    @asyncio.coroutine
    def getAgentMsgDirtyList(self, redisPool):
        # 获取代理数据
        with (yield from redisPool) as redis:
            listDirtyId = yield from redis.smembers(agentMsgKeyDirtyList)
            return listDirtyId

    @asyncio.coroutine
    def removeAgentMsgDirtyList(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem(agentMsgKeyDirtyList, remove_item)

    @asyncio.coroutine
    def getAgentMsgByMsgId(self, msgId):
        # 获取代理消息
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            bytesAgentMsg = yield from redis.hget("AgentMsgHash", msgId)
            if bytesAgentMsg is None:
                return None
            else:
                AgentMsgData = self.loads(self.bDebug, bytesAgentMsg)
            return AgentMsgData

    # 消息
    @asyncio.coroutine
    def addSysMsgKeyDirtyList(self, redisPool, MsgId):
        # TODO 等添加用户消息接口写好再接
        yield from redisPool.sadd(sysMsgKeyDirtyList, MsgId)

    # 后台增加系统消息
    @asyncio.coroutine
    def addSystemMsg(self, SystemMsgData: classMessageData):
        bytesSystemMsgData = self.dumps(self.bDebug, SystemMsgData)
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from self.addNewSysMsgToList(redis, SystemMsgData.strMsgId + '_' + SystemMsgData.strAccountId)
            # yield from self.addSysMsgKeyDirtyList(redis, SystemMsgData.strMsgId+'_'+SystemMsgData.strAccountId)
            yield from redis.zadd("SystemMsg", SystemMsgData.iMsgTime,
                                  SystemMsgData.strMsgId + '_' + SystemMsgData.strAccountId)
            yield from redis.hset("SystemMsgHash", SystemMsgData.strMsgId + '_' + SystemMsgData.strAccountId,
                                  bytesSystemMsgData)


    # 用户获取系统消息
    @asyncio.coroutine
    def getOneSystemMsg(self, MsgId: str, accountId: str):
        """获取详细信息"""
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            bytesSystemMsgData = yield from redis.hget("SystemMsgHash", MsgId + '_' + accountId)
            if bytesSystemMsgData is None:
                return None
            else:
                sysMsgData = self.loads(self.bDebug, bytesSystemMsgData)
                sysMsgData.iReadFlag = 1
                bytesSystemMsgData = self.dumps(self.bDebug, sysMsgData)
                yield from redis.hset("SystemMsgHash", MsgId + '_' + accountId, bytesSystemMsgData)
                return sysMsgData

    @asyncio.coroutine
    def delSystemMsg(self, MsgId: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from redis.zrem("SystemMsg", MsgId)
            yield from redis.hdel("SystemMsgHash", MsgId)

    @asyncio.coroutine
    def setNoticMsg(self, msgId, objNotice):
        bytesNotice = self.dumps(self.bDebug, objNotice)
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from redis.hset("type1_MsgHash", msgId, bytesNotice)
            yield from redis.sadd(noticeMsgKeyDirtyList, msgId)

    # 系统消息入库
    @asyncio.coroutine
    def addNewSysMsgToList(self, redisPool, systemMsgId):
        # 新增系统消息到队列
        yield from redisPool.sadd(sysMsgNewKeyList, systemMsgId)

    @asyncio.coroutine
    def getSysMsgNewList(self, redisPool):
        # 获取系统消息新列表
        with (yield from redisPool) as redis:
            listNewMsg = yield from redis.smembers(sysMsgNewKeyList)
            return listNewMsg

    @asyncio.coroutine
    def removeSysMsgNew(self, redisPool, remove_item):
        # 删除系统新信息
        with (yield from redisPool) as redis:
            yield from redis.srem(sysMsgNewKeyList, remove_item)

    @asyncio.coroutine
    def getSysMsgDirtyList(self, redisPool):
        # 获取系统数据
        with (yield from redisPool) as redis:
            listDirtyId = yield from redis.smembers(sysMsgKeyDirtyList)
            return listDirtyId

    @asyncio.coroutine
    def removeSysMsgDirtyList(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem(sysMsgKeyDirtyList, remove_item)

    @asyncio.coroutine
    def getSysMsgByMsgId(self, MsgId):
        # 获取用户消息
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            bytesSysMsg = yield from redis.hget("SystemMsgHash", MsgId)
            if bytesSysMsg is None:
                return None
            else:
                SysMsgData = self.loads(self.bDebug, bytesSysMsg)
            return SysMsgData

    @asyncio.coroutine
    def addNoticeMsgKeyDirtyList(self, redisPool, MsgId):
        yield from redisPool.sadd(noticeMsgKeyDirtyList, MsgId)

    @asyncio.coroutine
    def addNewsMsgKeyDirtyList(self, redisPool, MsgId):
        yield from redisPool.sadd(newsMsgKeyDirtyList, MsgId)

    @asyncio.coroutine
    def addMsg(self, type: int, MsgData: classMessageData, msgId: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            if type == 1:
                if len(msgId) <= 0:
                    yield from self.addNewNoticeMsgToList(redis, MsgData.strMsgId)
                else:
                    yield from self.addNoticeMsgKeyDirtyList(redis, msgId)
            elif type == 2:
                if len(msgId) <= 0:
                    yield from self.addNewNewsMsgToList(redis, MsgData.strMsgId)
                else:
                    yield from self.addNewsMsgKeyDirtyList(redis, msgId)
            bytesMsgData = self.dumps(self.bDebug, MsgData)
            yield from redis.zadd("type{}_MsgSortSet".format(type), MsgData.iMsgTime, MsgData.strMsgId)
            yield from redis.hset("type{}_MsgHash".format(type), MsgData.strMsgId, bytesMsgData)

    @asyncio.coroutine
    def getMsgCount(self, type: int):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            count = yield from redis.zcard("type{}_MsgSortSet".format(type))
            return count

    @asyncio.coroutine
    def getOneMsg(self, type: int, msgId: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            bytesMsgData = yield from redis.hget("type{}_MsgHash".format(type), msgId)
            if bytesMsgData is None:
                return None
            else:
                MsgData = self.loads(self.bDebug, bytesMsgData)
                return MsgData

    @asyncio.coroutine
    def getAllMsg(self, type: int):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            msgIdList = yield from redis.zrevrange("type{}_MsgSortSet".format(type), 0, -1)
            if msgIdList is None:
                return []
            else:
                msgDataList = []
                for msgId in msgIdList:
                    bytesMsgData = yield from redis.hget("type{}_MsgHash".format(type), msgId)
                    if bytesMsgData is None:
                        return None
                    else:
                        msgData = self.loads(self.bDebug, bytesMsgData)
                        msgDataList.append(msgData)
                return msgDataList

    @asyncio.coroutine
    def delMsg(self, type: int, msgId: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from redis.zrem("type{}_MsgSortSet".format(type), msgId)
            yield from redis.hdel("type{}_MsgHash".format(type), msgId)

    # 公告、新闻消息入库
    @asyncio.coroutine
    def addNewNoticeMsgToList(self, redisPool, noticeMsgId):
        # 新增公告消息到队列
        yield from redisPool.sadd(noticeMsgNewKeyList, noticeMsgId)

    @asyncio.coroutine
    def getNoticeMsgNewList(self, redisPool):
        # 获取新增公告消息队列
        with (yield from redisPool) as redis:
            newList = yield from redis.smembers(noticeMsgNewKeyList)
            return newList

    @asyncio.coroutine
    def getNoticeMsgByMsgId(self, type: int, MsgId: str):
        # 获取公告消息
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            bytesNoticeMsg = yield from redis.hget("type{}_MsgHash".format(type), MsgId)
            if bytesNoticeMsg is None:
                return None
            else:
                noticeMsg = self.loads(self.bDebug, bytesNoticeMsg)
            return noticeMsg

    @asyncio.coroutine
    def removeNoticeMsgNew(self, redisPool, remove_item):
        # 删除公告新信息
        with (yield from redisPool) as redis:
            yield from redis.srem(noticeMsgNewKeyList, remove_item)

    @asyncio.coroutine
    def getNoticeMsgDirtyList(self, redisPool):
        with (yield from redisPool) as redis:
            listDirtyId = yield from redis.smembers(noticeMsgKeyDirtyList)
            return listDirtyId

    @asyncio.coroutine
    def removeNoticeMsgDirtyList(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem(noticeMsgKeyDirtyList, remove_item)

    @asyncio.coroutine
    def addNewNewsMsgToList(self, redisPool, newsMsgId):
        # 新增新闻消息到队列
        yield from redisPool.sadd(newsMsgNewKeyList, newsMsgId)

    @asyncio.coroutine
    def getNewsMsgNewList(self, redisPool):
        # 获取新增的新闻消息队列
        with (yield from redisPool) as redis:
            news_list = yield from redis.smembers(newsMsgNewKeyList)
            return news_list

    @asyncio.coroutine
    def getNewsMsgByMsgId(self, type: int, MsgId: str):
        # 获取新闻消息
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            bytesNewsMsg = yield from redis.hget("type{}_MsgHash".format(type), MsgId)
            if bytesNewsMsg is None:
                return None
            else:
                newsMsg = self.loads(self.bDebug, bytesNewsMsg)
            return newsMsg

    @asyncio.coroutine
    def removeNewsMsgNew(self, redisPool, remove_item):
        # 删除新闻新信息
        with (yield from redisPool) as redis:
            yield from redis.srem(newsMsgNewKeyList, remove_item)

    @asyncio.coroutine
    def getNewsMsgDirtyList(self, redisPool):
        with (yield from redisPool) as redis:
            listDirtyId = yield from redis.smembers(newsMsgKeyDirtyList)
            return listDirtyId

    @asyncio.coroutine
    def removeNewsMsgDirtyList(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem(newsMsgKeyDirtyList, remove_item)

    # 用户
    @asyncio.coroutine
    def getAllPlayerId(self):
        """获取所有用户id"""
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            playerIdList = yield from redis.lrange("playerDataKeyDirtyList", 0, -1)
            if playerIdList is None:
                return None
            else:
                # return self.dumps(self.bDebug, bytesAllPlayerData)
                return playerIdList

    @asyncio.coroutine
    def setPhoneVerify(self, phone: str, iCode: int):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from redis.setex("phone_{}".format(phone), constants.SMS_CODE_REDIS_EXPIRES, iCode)

    @asyncio.coroutine
    def getPhoneVerify(self, phone: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            iCode = yield from redis.get("phone_%s" % phone)
            if iCode:
                return iCode.decode()
            else:
                return None

    @asyncio.coroutine
    def delPhoneVerify(self, phone: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from redis.delete("phone_%s" % phone)

    @asyncio.coroutine
    def setPhoneAccountMapping(self, phone: str, accountId: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from redis.hset("PhoneAccountHash", phone, accountId)

    @asyncio.coroutine
    def getPhoneAccountMapping(self, phone: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            accountId = yield from redis.hget("PhoneAccountHash", phone)
            if accountId:
                return accountId
            else:
                return None

    @asyncio.coroutine
    def setEmailVerify(self, Emial: str, iCode: int):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from redis.setex("email_{}".format(Emial), constants.SMS_CODE_REDIS_EXPIRES, iCode)

    @asyncio.coroutine
    def getEmailVerify(self, Email: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            iCode = yield from redis.get("email_%s" % Email)
            if iCode:
                return iCode.decode()
            else:
                return None

    @asyncio.coroutine
    def delEmailVerify(self, Email: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from redis.delete("email_%s" % Email)

    @asyncio.coroutine
    def setEmailAccountMapping(self, email: str, accountId: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from redis.hset("EmailAccountHash", email, accountId)

    @asyncio.coroutine
    def getEmailAccountMapping(self, email: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            accountId = yield from redis.hget("EmailAccountHash", email)
            if accountId:
                return accountId
            else:
                return None

    # 操盘后台统计分析用
    @asyncio.coroutine
    def addGraphBetRange(self, account_id: str, match_id: str, guess_id: str, bet_num: int, range_index: float,
                         strBetItemId: str, addTime: int, rate: float):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            objPipline = redis.pipeline()
            objPipline.hincrby("graphBetRange_{}_{}".format(guess_id, strBetItemId), str(range_index), bet_num)
            objPipline.hincrby("uniqueAccount_{}".format(guess_id), account_id, bet_num)
            objPipline.zadd("recentBetPlayer_{}".format(guess_id), addTime, json.dumps(
                {"id": account_id, "num": bet_num, "type": strBetItemId, "rate": rate, "time": addTime}))
            yield from objPipline.execute()

    # 开奖的一些接口调用
    @asyncio.coroutine
    def getSetResultRedisList(self, guess_id: str, team_key: str, incr_num: int):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            result = yield from redis.incrby("resultRedisListPos_{}_{}".format(guess_id, team_key), incr_num)
            return result

    @asyncio.coroutine
    def getResultRedisList(self, guess_id: str, team_key: str, begin_pos, end_pos):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            result = yield from redis.zrange("matchGuessMemberKey_{}".format(guess_id + '_' + team_key), begin_pos,
                                             end_pos)
            return result

    @asyncio.coroutine
    def getSetResultRedisListByScore(self, guess_id: str, team_key: str, incr_score: int):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            result = yield from redis.incrby("resultRedisListScore_{}_{}".format(guess_id, team_key), incr_score)
            return result

    @asyncio.coroutine
    def getResultRedisListByTime(self, guess_id: str, team_key: str, begin_time, end_time):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            result = yield from redis.zrangebyscore("matchGuessMemberKey_{}".format(guess_id + '_' + team_key),
                                                    begin_time, end_time)
            return result

    @asyncio.coroutine
    def getMatchCancelResultGuessUIds(self, guess_id):
        # 取消比赛的竞猜ids
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            guessUId = yield from redis.rpop("matchCancelResultGuessUIdList_{}".format(guess_id))
            if type(guessUId) is bytes:
                return guessUId.decode()
            else:
                return guessUId

    @asyncio.coroutine
    def getMatchSetResultGuessUIds(self, guess_id):
        # 重新开奖比赛的竞猜ids
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            guessUId = yield from redis.rpop("matchSetResultGuessUIdList_{}".format(guess_id))
            if type(guessUId) is bytes:
                return guessUId.decode()
            else:
                return guessUId

    @asyncio.coroutine
    def getPayOrderByLock(self, payOrder, reenTrantLock = None):
        if reenTrantLock is None:
            strLockId = str(uuid.uuid1())
        else:
            # 重入锁
            strLockId = reenTrantLock

        iTryCount = 5
        while iTryCount > 0:
            try:
                with (yield from self.dictAioRedis[miscConfig].getRedisPool()) as redis:

                    iTryCount -= 1
                    objPayDataBytes = yield from redis.evalsha(self.dictScriptNameSha['getDataByLock.lua'],
                                                               [payDataHash,
                                                                payLockIdKey.format(payOrder),
                                                                payLockTimeKey.format(payOrder)],
                                                               [payOrder, "True", strLockId, 500])

                    if objPayDataBytes is not None:
                        return self.loads(self.bDebug, objPayDataBytes), strLockId
                    else:
                        return None, ""
            except aioredis.errors.ReplyError as e:
                if e.args[0].find("locked"):
                    logging.error("payData orderId[{}] is lock".format(payOrder))
                    if iTryCount <= 0:
                        raise exceptionLogic(errorLogic.data_locked)
                    yield from asyncio.sleep(random.uniform(0, 0.3))
                    continue

    @asyncio.coroutine
    def releasePayDataLock(self, payOrder: str, lock: str):
        with (yield from self.dictAioRedis[miscConfig].getRedisPool()) as redis:
            # TODO 用lua 来修改用户数据
            yield from redis.delete(payLockIdKey.format(payOrder))

    @asyncio.coroutine
    def getPayOrder(self, payOrder):
        with (yield from self.dictAioRedis[miscConfig].getRedisPool()) as redis:
            objPayDataBytes = yield from redis.hget(payDataHash, payOrder)
            if objPayDataBytes is None:
                return None
            else:
                return self.loads(self.bDebug, objPayDataBytes)

    @asyncio.coroutine
    def setPayOrderByLock(self, payOrder, lock="", save=True, new=False):

        bytesPayData = self.dumps(self.bDebug, payOrder)
        with (yield from self.dictAioRedis[miscConfig].getRedisPool()) as redis:
            # TODO 换lua 文件，以后换成统一的lua
            yield from redis.evalsha(self.dictScriptNameSha['setPlayerDataByLock.lua'],
                                     [payDataHash,
                                      payDataKeyDirtyList,
                                      payDataKeyNewList,
                                      payLockIdKey.format(payOrder.strPayOrder),
                                      payLockTimeKey.format(payOrder.strPayOrder)],
                                     [payOrder.strPayOrder, bytesPayData, lock, str(save), str(new)])

    @asyncio.coroutine
    def getPayShortUrl(self, shortUrl):
        with (yield from self.dictAioRedis[miscConfig].getRedisPool()) as redis:
            longUrl = yield from redis.get(urlShortStr + shortUrl)
            if longUrl is None:
                return None
            else:
                return longUrl.decode()

    @asyncio.coroutine
    def setPayShortUrl(self, shortUrl, longUrl):
        with (yield from self.dictAioRedis[miscConfig].getRedisPool()) as redis:
            yield from redis.setex(urlShortStr + shortUrl, 30 * 60, longUrl)

    @asyncio.coroutine
    def getPayOrderDataNewList(self, redisPool):
        with (yield from redisPool) as redis:
            retList = yield from redis.smembers(payDataKeyNewList)
            if retList is None:
                return []
            return retList

    @asyncio.coroutine
    def getPayOrderDataDirtyList(self, redisPool):
        with (yield from redisPool) as redis:
            retList = yield from redis.smembers(payDataKeyDirtyList)
            if retList is None:
                return []
            return retList

    @asyncio.coroutine
    def removePayOrderNew(self, redisPool, remKey):
        with (yield from redisPool) as redis:
            yield from redis.srem(payDataKeyNewList, remKey)

    @asyncio.coroutine
    def removePayOrderDirty(self, redisPool, remKey):
        with (yield from redisPool) as redis:
            yield from redis.srem(payDataKeyDirtyList, remKey)

    # 平博维护
    @asyncio.coroutine
    def addRepairData(self, RepairData: classRepairData, repairId: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            bytesRepairData = self.dumps(self.bDebug, RepairData)
            if len(repairId) <= 0:
                yield from self.addNewRepairDataToList(redis, RepairData.strRepairId)
            else:
                yield from self.addRepairDataKeyDirtyList(redis, repairId)
            yield from redis.zadd("repairDataSortSet", RepairData.iTime,
                                  RepairData.strRepairId)
            yield from redis.hset("repairDataHash", RepairData.strRepairId, bytesRepairData)

    @asyncio.coroutine
    def getOneRepairData(self, repairId: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            bytesRepairData = yield from redis.hget("repairDataHash", repairId)
            if bytesRepairData is None:
                return None
            else:
                RepairData = self.loads(self.bDebug, bytesRepairData)
                return RepairData

    @asyncio.coroutine
    def addNewRepairDataToList(self, redisPool, repairId):
        # 新增维护信息到队列
        yield from redisPool.sadd(repairDataNewKeyList, repairId)

    @asyncio.coroutine
    def getRepairDataNewList(self, redisPool):
        # 获取维护新列表
        with (yield from redisPool) as redis:
            listNewRepair = yield from redis.smembers(repairDataNewKeyList)
            return listNewRepair

    @asyncio.coroutine
    def removeRepairDataNew(self, redisPool, remove_item):
        # 删除维护新信息
        with (yield from redisPool) as redis:
            yield from redis.srem(repairDataNewKeyList, remove_item)

    @asyncio.coroutine
    def addRepairDataKeyDirtyList(self, redisPool, repairId):
        # 添加维护数据
        yield from redisPool.sadd(repairDataKeyDirtyList, repairId)

    @asyncio.coroutine
    def removeRepairDataKeyDirtyList(self, redisPool, repairId):
        # 删除维护数据
        with (yield from redisPool) as redis:
            yield from redis.srem(repairDataKeyDirtyList, repairId)

    @asyncio.coroutine
    def getRepairDataDirtyList(self, redisPool):
        # 获取维护数据
        with (yield from redisPool) as redis:
            listDirtyId = yield from redis.smembers(repairDataKeyDirtyList)
            return listDirtyId

    @asyncio.coroutine
    def setCalcWaterPinboAccountId(self, listAccounts):
        with (yield from self.dictAioRedis[miscConfig].getRedisPool()) as redis:
            yield from redis.sadd(pinboLoginIdWaterDirtyList, *listAccounts)

    @asyncio.coroutine
    def getCalcWaterPinboAccountId(self):
        with (yield from self.dictAioRedis[miscConfig].getRedisPool()) as redis:
            listIds = yield from redis.smembers(pinboLoginIdWaterDirtyList)
            if listIds is None:
                return []
            else:
                return listIds

    @asyncio.coroutine
    def setCalcMonthWaterTime(self, iTime):
        with (yield from self.dictAioRedis[miscConfig].getRedisPool()) as redis:
            yield from redis.set(calcMonthWaterTimeStr, iTime)

    @asyncio.coroutine
    def getCalcMonthWaterTime(self):
        with (yield from self.dictAioRedis[miscConfig].getRedisPool()) as redis:
            iRet = yield from redis.get(calcMonthWaterTimeStr)
            if iRet is None:
                return 0
            else:
                return int(iRet)

    @asyncio.coroutine
    def setCalcDayWaterTime(self, iTime):
        with (yield from self.dictAioRedis[miscConfig].getRedisPool()) as redis:
            yield from redis.set(calcDayWaterTimeStr, iTime)

    @asyncio.coroutine
    def getCalcDayWaterTime(self):
        with (yield from self.dictAioRedis[miscConfig].getRedisPool()) as redis:
            iRet = yield from redis.get(calcDayWaterTimeStr)
            if iRet is None:
                return 0
            else:
                return int(iRet)

    @asyncio.coroutine
    def setRankDayWaterTime(self, iTime):
        with (yield from self.dictAioRedis[miscConfig].getRedisPool()) as redis:
            yield from redis.set(calcDayWaterTimeStr, iTime)

    @asyncio.coroutine
    def getRankDayWaterTime(self):
        with (yield from self.dictAioRedis[miscConfig].getRedisPool()) as redis:
            iRet = yield from redis.get(calcDayWaterTimeStr)
            if iRet is None:
                return 0
            else:
                return int(iRet)

    @asyncio.coroutine
    def setCalcMonthCommissionTime(self, iTime):
        with (yield from self.dictAioRedis[miscConfig].getRedisPool()) as redis:
            yield from redis.set(calcMonthCommissionTimeStr, iTime)

    @asyncio.coroutine
    def getCalcMonthCommissionTime(self):
        with (yield from self.dictAioRedis[miscConfig].getRedisPool()) as redis:
            iRet = yield from redis.get(calcMonthCommissionTimeStr)
            if iRet is None:
                return 0
            else:
                return int(iRet)

    @asyncio.coroutine
    def setCalcMonthByDayCommissionTime(self, iTime):
        with (yield from self.dictAioRedis[miscConfig].getRedisPool()) as redis:
            yield from redis.set(calcMonthByDayCommissionTimeStr, iTime)

    @asyncio.coroutine
    def getCalcMonthByDayCommissionTime(self):
        with (yield from self.dictAioRedis[miscConfig].getRedisPool()) as redis:
            iRet = yield from redis.get(calcMonthByDayCommissionTimeStr)
            if iRet is None:
                return 0
            else:
                return int(iRet)


    ###代理
    @asyncio.coroutine
    def setAgentData(self, agentData:classAgentData, new=False):
        bytesAgentData = self.dumps(self.bDebug, agentData)
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from redis.hset(agentDataHash, agentData.strAgentId, bytesAgentData)

    # 合营代码与代理id一一对应
    @asyncio.coroutine
    def setAgentCodeMapping(self, agentId, code):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from redis.hset("AgentCodeHash", code, agentId)

    @asyncio.coroutine
    def getAgentCodeMapping(self, code):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            agenttId = yield from redis.hget("AgentCodeHash", code)
            if agenttId:
                return agenttId.decode()
            else:
                return None

    @asyncio.coroutine
    def getAgentData(self, agentId: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            bytesAgentData = yield from redis.hget(agentDataHash, agentId)
            if bytesAgentData is None:
                return None
            else:
                return self.loads(self.bDebug, bytesAgentData)

    @asyncio.coroutine
    def addNewAgentToList(self, redisPool, agentId):
        with (yield from redisPool) as redis:
            yield from redis.sadd(agentDataKeyNewList, agentId)

    @asyncio.coroutine
    def getAgentDataNewList(self, redisPool):
        with (yield from redisPool) as redis:
            listNewId = yield from redis.smembers(agentDataKeyNewList)
            return listNewId

    @asyncio.coroutine
    def removeNewAgentList(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem(agentDataKeyNewList, remove_item)

    @asyncio.coroutine
    def addAgentToDirtyList(self, redisPool, agentId):
        with (yield from redisPool) as redis:
            yield from redis.sadd(agentDataKeyDirtyList, agentId)

    @asyncio.coroutine
    def getAgentDataDirtyList(self, redisPool):
        with (yield from redisPool) as redis:
            listDirtyId = yield from redis.smembers(agentDataKeyDirtyList)
            return listDirtyId

    @asyncio.coroutine
    def removeAgentDirtyList(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem(agentDataKeyDirtyList, remove_item)



    @asyncio.coroutine
    def getActiveDataByLock(self, strAccountId, reenTrantLock=None):
        if reenTrantLock is None:
            strLockId = str(uuid.uuid1())
        else:
            # 重入锁
            strLockId = reenTrantLock

        iTryCount = 5
        while iTryCount > 0:
            try:
                with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:

                    iTryCount -= 1
                    objActiveDataBytes = yield from redis.evalsha(self.dictScriptNameSha['getDataByLock.lua'],
                                                               [activeDataHash,
                                                                activeLockIdKey.format(strAccountId),
                                                                activeLockTimeKey.format(strAccountId)],
                                                               [strAccountId, "True", strLockId, 500])

                    if objActiveDataBytes is not None:
                        return self.loads(self.bDebug, objActiveDataBytes), strLockId
                    else:
                        return None, ""
            except aioredis.errors.ReplyError as e:
                if e.args[0].find("locked"):
                    logging.error("activeData AccountId[{}] is lock".format(strAccountId))
                    if iTryCount <= 0:
                        raise exceptionLogic(errorLogic.data_locked)
                    yield from asyncio.sleep(random.uniform(0, 0.3))
                    continue

    @asyncio.coroutine
    def getActiveData(self, strAccountId):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            objActiveDataBytes = yield from redis.hget(activeDataHash, strAccountId)
            if objActiveDataBytes is None:
                return None
            else:
                return self.loads(self.bDebug, objActiveDataBytes)

    @asyncio.coroutine
    def setActiveDataByLock(self, activeData, lock="", save=True, new=False):

        bytesPayData = self.dumps(self.bDebug, activeData)
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            # TODO 换lua 文件，以后换成统一的lua
            yield from redis.evalsha(self.dictScriptNameSha['setPlayerDataByLock.lua'],
                                     [activeDataHash,
                                      activeDataKeyDirtyList,
                                      activeDataKeyNewList,
                                      activeLockIdKey.format(activeData.strAccountId),
                                      activeLockTimeKey.format(activeData.strAccountId)],
                                     [activeData.strAccountId, bytesPayData, lock, str(save), str(new)])

    @asyncio.coroutine
    def releaseActiveDataLock(self, accountId: str, lock: str):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            # TODO 用lua 来修改用户数据
            yield from redis.delete(activeLockIdKey.format(accountId))

    @asyncio.coroutine
    def addNewActiveToList(self, redisPool, agentId):
        with (yield from redisPool) as redis:
            yield from redis.sadd(activeDataKeyNewList, agentId)

    @asyncio.coroutine
    def getActiveDataNewList(self, redisPool):
        with (yield from redisPool) as redis:
            listNewId = yield from redis.smembers(activeDataKeyNewList)
            return listNewId

    @asyncio.coroutine
    def removeNewActiveList(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem(activeDataKeyNewList, remove_item)

    @asyncio.coroutine
    def addActiveToDirtyList(self, redisPool, agentId):
        with (yield from redisPool) as redis:
            yield from redis.sadd(activeDataKeyDirtyList, agentId)

    @asyncio.coroutine
    def getActiveDataDirtyList(self, redisPool):
        with (yield from redisPool) as redis:
            listDirtyId = yield from redis.smembers(activeDataKeyDirtyList)
            return listDirtyId

    @asyncio.coroutine
    def removeActiveDirtyList(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem(activeDataKeyDirtyList, remove_item)

    # 添加佣金数据
    @asyncio.coroutine
    def addAgentCommissionData(self, commissionData: classAgentCommissionData, billId=None):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            objPipline = redis.pipeline()
            objPipline.zadd("agentCommissionSortKey", commissionData.iTime,
                            commissionData.strBillId)
            objPipline.hset("agentCommissionHashKey", commissionData.strBillId,
                            self.dumps(self.bDebug, commissionData))
            if not billId:
                objPipline.sadd("agentCommissionKey_New", commissionData.strBillId)
            else:
                objPipline.sadd("agentCommissionKey_Dirty", billId)
            yield from objPipline.execute()

    # 获取佣金账单数据
    @asyncio.coroutine
    def getCommissionData(self, billId):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            ret = yield from redis.hget("agentCommissionHashKey", billId)
            if ret is None:
                return None
            else:
                return self.loads(self.bDebug, ret)

    # 获取新产生的佣金账单数据
    @asyncio.coroutine
    def getAgentCommissionDataNewList(self, redisPool):
        with (yield from redisPool) as redis:
            listNewCommissionDataIds = yield from redis.smembers("agentCommissionKey_New")
            return listNewCommissionDataIds

    # 获取佣金账单数据
    @asyncio.coroutine
    def getAgentCommissionData(self, billId, redisPool):
        with (yield from redisPool) as redis:
            ret = yield from redis.hget("agentCommissionHashKey", billId)
            if ret is None:
                return None
            else:
                return self.loads(self.bDebug, ret)

    # 删除佣金帐单新数据
    @asyncio.coroutine
    def removeAgentCommissionDataNew(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem("agentCommissionKey_New", remove_item)

    # 获取新佣金帐单数据
    @asyncio.coroutine
    def getAgentCommissionDataDirtyList(self, redisPool):
        with (yield from redisPool) as redis:
            listNewCommissionDataIds = yield from redis.smembers("agentCommissionKey_Dirty")
            return listNewCommissionDataIds

    # 删除佣金账单数据
    @asyncio.coroutine
    def removeAgentCommissionDataDirty(self, redisPool, remove_item):
        with (yield from redisPool) as redis:
            yield from redis.srem("agentCommissionKey_Dirty", remove_item)

    # 代理申请
    @asyncio.coroutine
    def setApplyInfo(self, applyInfo):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            bytesApplyInfo = self.dumps(self.bDebug, applyInfo)
            yield from redis.hset("applyInfoHash", applyInfo.strAgentId, bytesApplyInfo)

    # 合营代码集合
    @asyncio.coroutine
    def setCid(self, cid):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from redis.sadd("agentCidSet", cid)

    # 检查合营代码在不在集合中，防止重复
    @asyncio.coroutine
    def checkCid(self,cid):
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            ret = yield from redis.sismember("agentCidSet", cid)
            return ret

    @asyncio.coroutine
    def addAgentConfig(self, configData: classConfig):
        # 新增、修改代理费率设置
        bytesConfigData = self.dumps(self.bDebug, configData)
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from redis.hset('AgentConfigHash', configData.strName, bytesConfigData)

    @asyncio.coroutine
    def delAgentConfig(self, configName):
        # 删除代理config
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            ret=yield from redis.hdel('AgentConfigHash', configName)
            return ret

    @asyncio.coroutine
    def getAgentConfig(self):
        # 获取代理config
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            ret = yield from redis.hvals('AgentConfigHash')
            listAgent=[]
            for bytesAgent in ret:
                agent=self.loads(self.bDebug,bytesAgent)
                listAgent.append(agent)
            return listAgent

    @asyncio.coroutine
    def addUpdatePingboAccountId(self,accountId):
        #新增待拉取平博钱包数据的账号
        with (yield from self.dictAioRedis[userConfig].getRedisPool()) as redis:
            yield from redis.sadd('UpdatePingboCoinSet',accountId)

    @asyncio.coroutine
    def getUpdatePingboAccountId(self,redisPool):
        with (yield from redisPool) as redis:
            ret=yield from redis.spop('UpdatePingboCoinSet')
            return ret