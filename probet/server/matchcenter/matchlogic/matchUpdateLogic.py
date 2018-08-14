import asyncio
import logging
from lib.timehelp import timeHelp
from datawrapper.dataBaseMgr import classDataBaseMgr

@asyncio.coroutine
def updateMatchState():
    objRedis = classDataBaseMgr.getInstance()
    iNowTime = timeHelp.getNow()

    # 获取当前比赛的数据
    listMatchData = yield from objRedis.getMatchDataListByScore(0,-1,"all")

    iMatchIndex = 0
    for iIndex in range(0, len(listMatchData)):
        try:
            var_match = listMatchData[iIndex]

            if var_match.iMatchState == 3:
                continue

            if iNowTime >= var_match.iMatchStartTimestamp:
                if var_match.iMatchState < 2:
                    # 如果状态没有被 数据中心回调，这里继续增加竞猜延迟
                    objMatchData,objMatchLock = yield from objRedis.getMatchDataByLock(var_match.strMatchId)
                    objMatchData.iMatchState = 2
                    yield from classDataBaseMgr.getInstance().setMatchDataByLock(objMatchData,objMatchLock)
            else:
                pass

        finally:
            iMatchIndex += 1