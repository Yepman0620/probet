import aioredis
import asyncio
import pickle
import threading


class classSubMgr():


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

    def stop(self):
        self.bRunFlag = False

    def __init__(self,call_name:str,address,pwd:str,dbIndex:int,aioLoop):

        self.strSubName = call_name

        self.callFunction = None

        self.setAddress = address
        self.iDb = dbIndex
        self.strPwd = pwd
        self.objAioLoopObj = aioLoop
        self.objAioRedis = None
        self.objSubChanel= None
        self.bRunFlag = True


    @asyncio.coroutine
    def connectRedis(self):

        self.objAioRedis = yield from aioredis.create_redis(address=self.setAddress, loop=self.objAioLoopObj,
                                                           db=self.iDb,
                                                           password=self.strPwd)

        res = yield from self.objAioRedis.subscribe(self.strSubName)
        self.objSubChanel = res[0]


    def registerCall(self,coroutineFunction):
        self.callFunction = coroutineFunction

    @asyncio.coroutine
    def updatePubSubChannel(self):
        while self.bRunFlag:

            while(yield from self.objSubChanel.wait_message()):
                msg = yield from self.objSubChanel.get()
                listMsg = pickle.loads(msg)

                yield from self.callFunction(listMsg[0], listMsg[1])
