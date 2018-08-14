import aioredis
import asyncio
import pickle



class classResultPubSubMgr():
    def __init__(self,call_name:str,address,pwd:str,dbIndex:int,aioLoop):

        self.strSubName = call_name

        self.callFunction = None

        self.setAddress = address
        self.iDb = dbIndex
        self.strPwd = pwd
        self.objAioLoopObj = aioLoop
        self.objAioRedis = None
        self.objSubChanel= None

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
        while True:

            while(yield from self.objSubChanel.wait_message()):
                msg = yield from self.objSubChanel.get()
                listMsg = pickle.loads(msg)

                yield from self.callFunction(listMsg[0], listMsg[1])
