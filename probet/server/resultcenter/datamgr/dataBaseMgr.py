import asyncio
from gm.datamgr.dataBaseMgr import classGmDataBaseMgr
from config.zone_config import matchConfig


class classResultBaseMgr(classGmDataBaseMgr):
    def __init__(self,*args,**kwargs):
        super(classResultBaseMgr,self).__init__(*args,**kwargs)

    @asyncio.coroutine
    def getSetResultRedisList(self,guess_id:str,team_key:str,incr_num:int):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            result  = yield from redis.incrby("resultRedisListPos_{}_{}".format(guess_id,team_key),incr_num)
            return result

    @asyncio.coroutine
    def getResultRedisList(self,guess_id:str,team_key:str,begin_pos,end_pos):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:

            result  = yield from redis.zrange("matchGuessMemberKey_{}".format(guess_id+'_'+team_key),begin_pos,end_pos)
            return result


    @asyncio.coroutine
    def getSetResultRedisListByScore(self,guess_id:str,team_key:str,incr_score:int):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            result  = yield from redis.incrby("resultRedisListScore_{}_{}".format(guess_id,team_key),incr_score)
            return result


    @asyncio.coroutine
    def getResultRedisListByTime(self, guess_id: str, team_key: str, begin_time, end_time):
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            result = yield from redis.zrangebyscore("matchGuessMemberKey_{}".format(guess_id + '_' + team_key), begin_time, end_time)
            return result

    @asyncio.coroutine
    def getMatchCancelResultGuessUIds(self, guess_id):
        # 取消比赛的竞猜ids
        with (yield from self.dictAioRedis[matchConfig].getRedisPool()) as redis:
            guessUId =  yield from redis.rpop("matchCancelResultGuessUIdList_{}".format(guess_id))
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