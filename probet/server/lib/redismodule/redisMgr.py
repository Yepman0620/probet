import aioredis
import asyncio
from uhashring import HashRing


class  classAioRedis():
    def __init__(self,address, pwd:str,dbIndex:int,aioLoop,minPoolSize:int=5,maxPoolSize:int=5,encoding=None,*args, **kwargs):
        if isinstance(address,list):

            self.setAddressList = address
            self.setAddress = ""
            self.bHashRing = True
            self.objHashRing = HashRing([(ad[0] +':'+ str(ad[1])) for ad in address])

        else:
            self.setAddress = address
            self.setAddressList = []
            self.bHashRing = False

        self.iDb = dbIndex
        self.strPwd = pwd
        self.objAioLoopObj = aioLoop
        self.objAioRedis = None
        self.objAioRedisDict = {}
        self.iMinPoolSize = minPoolSize
        self.iMaxPoolSize = maxPoolSize
        self.strEncodeing = encoding

        self.dictScriptNameSha = {}


    @asyncio.coroutine
    def connectRedis(self):

        if len(self.setAddressList) > 0:

            for var_address in self.setAddressList:
                # TODO encoding=utf-8
                try:
                    objRedisPool = yield from aioredis.create_pool(address=var_address, loop=self.objAioLoopObj,
                                                                       db=self.iDb,
                                                                       password=self.strPwd, minsize=self.iMinPoolSize,
                                                                       maxsize=self.iMaxPoolSize,encoding=self.strEncodeing)

                    self.objAioRedisDict[(var_address[0]+":"+str(var_address[1]))] = objRedisPool


                except Exception as e:
                    print("aioredis init failed address{} port{} db{} pwd{}".format(var_address[0],var_address[1],self.iDb, self.strPwd))

                    raise e


        else:

            #TODO encoding=utf-8
            try:
                self.objAioRedis = yield from aioredis.create_pool(address=self.setAddress,loop=self.objAioLoopObj,db=self.iDb,
                                                  password=self.strPwd,minsize=self.iMinPoolSize,maxsize=self.iMaxPoolSize,encoding=self.strEncodeing)

            except Exception as e:
                print("aioredis init failed address{} port{} db{} pwd{}".format(self.setAddress[0],self.setAddress[1],
                                                                                    self.iDb,self.strPwd))

                raise e


    def getHashRingRedis(self,key):
        strServerAddress = self.objHashRing.get(key)
        #TODO raise redisMgr error
        return self.objAioRedisDict.get(strServerAddress,None)


    def getRedisPoolByKey(self,key):
        if self.bHashRing:
            strServerAddress = self.objHashRing.get(key)
            # TODO raise redisMgr error
            return self.objAioRedisDict.get(strServerAddress['hostname'], None)
        else:
            raise RuntimeError('not hash ring hash')

    def getAllRedisPool(self):
        if self.bHashRing:
            listNodes = self.objHashRing.get_nodes()
            listPool = []
            for var in listNodes:
                listPool.append(self.objAioRedisDict.get(var))
            return listPool
        else:
            raise RuntimeError('not hash ring hash')

    def getRedisPool(self):
        return self.objAioRedis