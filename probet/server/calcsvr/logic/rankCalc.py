from lib.timehelp import timeHelp
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.playerDataOpWrapper import addPlayerBill
from logic.enum.enumCoinOp import CoinOp
from config.vipConfig import vip_config
import asyncio
import logging


#每天中午进行反流水红利
@asyncio.coroutine
def calcRank():

    strLastCheckTime = yield from classDataBaseMgr.getInstance().getRankDayWaterTime()
    if strLastCheckTime is None:
        yield from classDataBaseMgr.getInstance().setCalcDayWaterTime(timeHelp.getNow())

    iLastCheckTime = int(strLastCheckTime)

    if not timeHelp.isSameHour(iLastCheckTime,timeHelp.getNow()):
        #一个小时计算一次
        yield from classDataBaseMgr.getInstance().setRankDayWaterTime(timeHelp.getNow())

