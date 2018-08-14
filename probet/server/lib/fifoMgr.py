from lib.redismodule.redisMgr import classAioRedis

import asyncio
import pickle
import logging
import threading

class classFIFOMgr(classAioRedis):


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

    def __init__(self,publish_name:str,call_name:str,*args,**kwargs):
        super(classFIFOMgr,self).__init__(*args,**kwargs)
        self.strPublisName = publish_name
        self.strCallName = call_name
        #self.strPushName = push_name

        self.callFunction = None
        self.iTickNum = 0
        self.bDebug = False
        self.bRunFlag = True

    @asyncio.coroutine
    def cleanFifoQueue(self):
        #with await self.objAioRedis as redis:
        with (yield from self.objAioRedis) as redis:
            yield from redis.delete(self.strPublisName)
            yield from redis.delete(self.strCallName)

    @asyncio.coroutine
    def publish(self,head,body):
        with (yield from self.objAioRedis) as redis:
            pushBuff = pickle.dumps([head,body])
            yield from redis.lpush(self.strPublisName,pushBuff)


    @asyncio.coroutine
    def get(self):
        with (yield from self.objAioRedis) as redis:
            list_size = yield from redis.llen(self.strCallName)
            if list_size > 100:
                logging.getLogger('logic').error("fifoname[{}] get list size[{}]".format(self.strCallName, list_size))
                list_size = 100

            #判断队列长度以后这个列表的内容可能被别的进程取走了,下面逻辑拿到的可能会有None的元素
            #TODO 优化操作

            objPipline = redis.pipeline()
            for index in range(0, list_size):
                objPipline.rpop(self.strCallName)
                #objPipline.rpop(self.strCallName)

            result = yield from objPipline.execute()

            # result = yield from redis.rpop(self.strCallName)
            if result == None:
                return []
            else:
                # ret = pickle.loads(result)
                return result


    def stop(self):
        self.bRunFlag = False


    def registerCall(self,coroutineFunction):
        self.callFunction = coroutineFunction

    @asyncio.coroutine
    def updateFifoChannel(self):
        while self.bRunFlag:
            try:
                result = yield from self.get()

                for var_msg in result:
                    if var_msg is None:
                        continue
                    msg = pickle.loads(var_msg)
                    head = msg[0]
                    body = msg[1]

                    #if head != None and body != None:
                        #print("callFunction")
                    yield from self.callFunction(head, body)

                if self.bDebug:
                    yield from asyncio.sleep(0.1)
                else:
                    yield from asyncio.sleep(0.01)
            except Exception as e:
                logging.exception(e)
                # TODO 这里先break，以前版本aioredis 停服不会走到这里面
                #break



