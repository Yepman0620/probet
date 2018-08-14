from lib.redismodule.redisMgr import classAioRedis
import asyncio
import pickle
import threading

class classPubMgr(classAioRedis):

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



    def __init__(self,publish_name:str,*args,**kwargs):
        super(classPubMgr, self).__init__(*args, **kwargs)
        self.strPublisName = publish_name

    @asyncio.coroutine
    def publish(self,head,body):
        pushBuff = pickle.dumps([head, body])
        with (yield from self.objAioRedis) as redis:
            yield from redis.publish(self.strPublisName,pushBuff)
