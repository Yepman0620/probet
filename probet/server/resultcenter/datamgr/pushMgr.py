import asyncio
import pickle
from lib.redismodule.redisMgr import classAioRedis
from error.errorDefine import exceptionLogInit
from config.zone_config import pushConfig,onlineConfig

class classPushMgr():
    def __init__(self,redisConfig,aioLoop,minPoolSize:int=5,maxPoolSize:int=5):

        self.dictAioRedis = {}

        for var_key, var_config in redisConfig.items():

            if var_config['hashRing'] != 0:
                if not isinstance(var_config['address'], list):
                    raise exceptionLogInit("redis config error")

            self.dictAioRedis[var_key] = classAioRedis(var_config['address'],
                                                       var_config['pwd'], var_config['dbIndex'],
                                                       aioLoop, minPoolSize, maxPoolSize)

        #self.strPushName = pushName


    @asyncio.coroutine
    def connectRedis(self):
        for var_key, var_aio_obj in self.dictAioRedis.items():
            yield from var_aio_obj.connectRedis()


    @asyncio.coroutine
    def push(self,host:str,group_id:int,head,body):
        with (yield from self.dictAioRedis[pushConfig].getRedisPool()) as redis:
            pushBuff = pickle.dumps([head, body])

            yield from redis.lpush("pushDataKey_{}_{}".format(host,group_id), pushBuff)
