import asyncio
import logging

from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic, errorLogic

@asyncio.coroutine
def getPingboValidWaterByParams(loginIds,startTime:int,endTime:int,agentId=None,betType=None):
    #根据条件获取平博的有效流水
    startTime=startTime-12*3600
    endTime=endTime-12*3600
    conn = classSqlBaseMgr.getInstance(instanceName='probet_oss')
    if loginIds:
        if isinstance(loginIds,list):
            if len(loginIds) == 1:
                Ids = str(tuple(loginIds)).replace(r',', '', 1)
            else:
                Ids = tuple(loginIds)
            pin_eu_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE odds>=1.5 AND oddsFormat=1 AND loginId in {} AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} ".format(
                Ids, startTime , endTime )
            pin_am_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE (-200<=odds<0 OR odds>=50) AND oddsFormat=0 AND loginId in {} AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} ".format(
                Ids, startTime , endTime)
            pin_my_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE (0.5<=odds<0 OR 0>odds>-1) AND oddsFormat=4 AND loginId in {} AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} ".format(
                Ids, startTime, endTime)
            pin_id_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE odds>=-2 AND oddsFormat=3 AND loginId in {} AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} ".format(
                Ids, startTime, endTime)
            pin_hk_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE odds>=0.5 AND oddsFormat=2 AND loginId in {} AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} ".format(
                Ids, startTime, endTime)
        else:
            pin_eu_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE odds>=1.5 AND oddsFormat=1 AND loginId in ("+loginIds+") AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} ".format(
                 startTime, endTime)
            pin_am_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE (-200<=odds<0 OR odds>=50) AND oddsFormat=0 AND loginId in ("+loginIds+") AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} ".format(
                 startTime, endTime)
            pin_my_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE (0.5<=odds<0 OR 0>odds>-1) AND oddsFormat=4 AND loginId in ("+loginIds+") AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} ".format(
                 startTime, endTime)
            pin_id_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE odds>=-2 AND oddsFormat=3 AND loginId in ("+loginIds+") AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} ".format(
                 startTime, endTime)
            pin_hk_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE odds>=0.5 AND oddsFormat=2 AND loginId in ("+loginIds+") AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} ".format(
                 startTime, endTime)
    else:
        if agentId:
            pin_eu_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE odds>=1.5 AND oddsFormat=1  AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} AND agentId='{}' ".format(
                startTime, endTime,agentId)
            pin_am_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE (-200<=odds<0 OR odds>=50) AND oddsFormat=0 AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} AND agentId='{}'".format(
                startTime, endTime,agentId)
            pin_my_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE (0.5<=odds<0 OR 0>odds>-1) AND oddsFormat=4 AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} AND agentId='{}'".format(
                startTime, endTime,agentId)
            pin_id_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE odds>=-2 AND oddsFormat=3 AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} AND agentId='{}'".format(
                startTime, endTime,agentId)
            pin_hk_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE odds>=0.5 AND oddsFormat=2 AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} AND agentId='{}'".format(
                startTime, endTime,agentId)
            if betType:
                pin_eu_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE odds>=1.5 AND oddsFormat=1  AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} AND betType={} ".format(
                    startTime, endTime, betType)
                pin_am_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE (-200<=odds<0 OR odds>=50) AND oddsFormat=0 AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} AND betType={}".format(
                    startTime, endTime, betType)
                pin_my_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE (0.5<=odds<0 OR 0>odds>-1) AND oddsFormat=4 AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} AND betType={}".format(
                    startTime, endTime, betType)
                pin_id_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE odds>=-2 AND oddsFormat=3 AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} AND betType={}".format(
                    startTime, endTime, betType)
                pin_hk_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE odds>=0.5 AND oddsFormat=2 AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} AND betType={}".format(
                    startTime, endTime, betType)
        else:
            pin_eu_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE odds>=1.5 AND oddsFormat=1  AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} ".format(
                startTime, endTime)
            pin_am_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE (-200<=odds<0 OR odds>=50) AND oddsFormat=0 AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} ".format(
                startTime, endTime)
            pin_my_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE (0.5<=odds<0 OR 0>odds>-1) AND oddsFormat=4 AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} ".format(
                startTime, endTime)
            pin_id_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE odds>=-2 AND oddsFormat=3 AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} ".format(
                startTime, endTime)
            pin_hk_valid_water_sql = "select sum(toRisk) from dj_pingbobetbill WHERE odds>=0.5 AND oddsFormat=2 AND status='SETTLED' AND wagerDateFm BETWEEN {} AND {} ".format(
                startTime, endTime)

    try:
        pin_am_valid_water=yield from conn._exeCute(pin_am_valid_water_sql)
        pin_eu_valid_water=yield from conn._exeCute(pin_eu_valid_water_sql)
        pin_hk_valid_water=yield from conn._exeCute(pin_hk_valid_water_sql)
        pin_id_valid_water=yield from conn._exeCute(pin_id_valid_water_sql)
        pin_my_valid_water=yield from conn._exeCute(pin_my_valid_water_sql)

        am_valid_water=yield from pin_am_valid_water.fetchone()
        eu_valid_water=yield from pin_eu_valid_water.fetchone()
        hk_valid_water=yield from pin_hk_valid_water.fetchone()
        id_valid_water=yield from pin_id_valid_water.fetchone()
        my_valid_water=yield from pin_my_valid_water.fetchone()

        amValidWater=0 if am_valid_water[0] is None else am_valid_water[0]
        euValidWater = 0 if eu_valid_water[0] is None else eu_valid_water[0]
        idValidWater = 0 if id_valid_water[0] is None else id_valid_water[0]
        myValidWater = 0 if my_valid_water[0] is None else my_valid_water[0]
        hkValidWater = 0 if hk_valid_water[0] is None else hk_valid_water[0]

        pingboValidWater=amValidWater+euValidWater+idValidWater+hkValidWater+myValidWater
        return pingboValidWater
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)