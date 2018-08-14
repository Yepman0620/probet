from lib.redismodule.redisMgr import classAioRedis
from error.errorDefine import exceptionLogInit
from config.zone_config import pushConfig,onlineConfig
import asyncio
import json


class classOnlineMgr():
    def __init__(self,redisConfig,aioLoop,minPoolSize:int=5,maxPoolSize:int=5):

        self.dictAioRedis = {}

        for var_key, var_config in redisConfig.items():

            if var_config['hashRing'] != 0:
                if not isinstance(var_config['address'], list):
                    raise exceptionLogInit("redis config error")

            self.dictAioRedis[var_key] = classAioRedis(var_config['address'],
                                                       var_config['pwd'], var_config['dbIndex'],
                                                       aioLoop, minPoolSize, maxPoolSize)

    @asyncio.coroutine
    def connectRedis(self):
        for var_key, var_aio_obj in self.dictAioRedis.items():
            yield from var_aio_obj.connectRedis()

    @asyncio.coroutine
    def setOnlineClient(self,account_id:str,group_id:int,host:str,udid:str,deviceModal:str,deviceName:str,connectUid:str):
        with (yield from self.dictAioRedis[onlineConfig].getRedisPool()) as redis:
            if len(account_id) > 0:
                objPipline = redis.pipeline()
                objPipline.set("onlineClientAccountKey_{}".format(account_id),json.dumps({"groupId":group_id,"host":host,"udid":udid,
                                                                                      "deviceModal": deviceModal,
                                                                                      "deviceName": deviceName,
                                                                                      "connectUid":connectUid}))
                objPipline.set("onlineClientUdidKey_{}".format(connectUid), account_id)
                objPipline.expire("onlineClientAccountKey_{}".format(account_id),86400 * 3)
                objPipline.expire("onlineClientUdidKey_{}".format(connectUid),86400 * 3)
                yield from objPipline.execute()

    @asyncio.coroutine
    def delOnlineClientMap(self,account_id:str):
        with (yield from self.dictAioRedis[onlineConfig].getRedisPool()) as redis:
            if len(account_id) > 0:
                yield from redis.delete("onlineClientAccountKey_{}".format(account_id))

    @asyncio.coroutine
    def getOnlineClient(self,account_id:str):
        with (yield from self.dictAioRedis[onlineConfig].getRedisPool()) as redis:
            bytesAccountOnline = yield from redis.get("onlineClientAccountKey_{}".format(account_id))
            if bytesAccountOnline is None:
                return None

            dictAccountOnline = json.loads(bytesAccountOnline)
            return dictAccountOnline


    @asyncio.coroutine
    def setOnlineUdid2Account(self,connectUid:str,account_id:str):
        with (yield from self.dictAioRedis[onlineConfig].getRedisPool()) as redis:
            yield from redis.set("onlineClientUdidKey_{}".format(connectUid),account_id)
            yield from redis.expire("onlineClientUdidKey_{}".format(connectUid), 86400 * 3)


    @asyncio.coroutine
    def getOnlineUdid2Account(self,connectUid:str):
        with (yield from self.dictAioRedis[onlineConfig].getRedisPool()) as redis:
            bytesAccountId = yield from redis.get("onlineClientUdidKey_{}".format(connectUid))
            if bytesAccountId is None:
                return None
            else:
                return bytesAccountId.decode()

    @asyncio.coroutine
    def delOnlineUdid2Account(self, connectUid: str):
        with (yield from self.dictAioRedis[onlineConfig].getRedisPool()) as redis:
            yield from redis.delete("onlineClientUdidKey_{}".format(connectUid))