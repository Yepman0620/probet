import asyncio
import pickle
from lib.redismodule.redisMgr import classAioRedis
from config.zoneConfig import pushConfig
import threading


class classPushMgr():

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
            return cls._instance.get(cls._defaultInstance,None)
        else:
            return cls._instance.get(instanceName,None)


    def __init__(self,redisConfig,aioLoop,minPoolSize:int=5,maxPoolSize:int=5):

        self.dictAioRedis = {}

        for var_key, var_config in redisConfig.items():

            if var_config['hashRing'] != 0:
                if not isinstance(var_config['address'], list):
                    raise RuntimeError("redis config error")

            self.dictAioRedis[var_key] = classAioRedis(var_config['address'],
                                                       var_config['pwd'], var_config['dbIndex'],
                                                       aioLoop, minPoolSize, maxPoolSize)

    @asyncio.coroutine
    def connectRedis(self):
        for var_key, var_aio_obj in self.dictAioRedis.items():
            yield from var_aio_obj.connectRedis()


    @asyncio.coroutine
    def push(self,host:str,group_id:int,head,body):
        with (yield from self.dictAioRedis[pushConfig].getRedisPool()) as redis:
            pushBuff = pickle.dumps([head, body])

            yield from redis.lpush("pushDataKey_{}_{}".format(host,group_id), pushBuff)
