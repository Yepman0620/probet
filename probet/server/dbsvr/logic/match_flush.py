from datetime import datetime
from lib.timehelp import timeHelp
import aiomysql
import asyncio
import logging

from config.zoneConfig import matchConfig
from logic.data.matchData import classMatchData
from datawrapper.dataBaseMgr import classDataBaseMgr
import sqlalchemy as sa


"""
metadata = sa.MetaData()

tbl = sa.Table(
    'dj_match', metadata,
    sa.Column('matchId', sa.String(255), default="",primary_key=True),
    sa.Column('matchTeamALogo', sa.String(255), default="",nullable=False),
    sa.Column('teamAName', sa.String(255), default="",nullable=False),
    sa.Column('matchTeamBLogo', sa.String(255), default="",nullable=False),
    sa.Column('teamBName', sa.String(255), default="",nullable=False),
    sa.Column('matchName', sa.String(255), default="",nullable=False),
    #sa.Column('matchBO', sa.Integer(), default=""),
    sa.Column('matchState', sa.Integer(), default=0,nullable=False,index=True),
    sa.Column('teamAScore', sa.Integer(), default=0,nullable=False),
    sa.Column('teamBScore', sa.Integer(), default=0,nullable=False),
    sa.Column('matchStartTime', sa.Integer(), default=0,nullable=False,index=True),
    sa.Column('matchEndTime', sa.Integer(), default=0,nullable=False),
    sa.Column('matchRoundNum',sa.Integer(),default=0,nullable=False),
)
"""
from gmweb.utils.models import Base
tbl = Base.metadata.tables["dj_match"]

#把mysql查出来的数据，转成classMatchData
def buildSqlResult2ClassMatch(fetchRowData):
    objNewData = classMatchData()
    objNewData.strMatchId = fetchRowData.matchId
    #objNewData.strMatchType =
    #objNewData.


@asyncio.coroutine
def doCheck():

    from datawrapper.sqlBaseMgr import classSqlBaseMgr
    engine = classSqlBaseMgr.getInstance().getEngine()
    with (yield from engine) as conn:
        # 检查写入新信息
        var_aio_redis = classDataBaseMgr.getInstance().dictAioRedis[matchConfig].objAioRedis

        try:
            # new_match_list = yield from classDataBaseMgr.getInstance().getAccountDataNewList(var_aio_redis)
            new_match_list = yield from classDataBaseMgr.getInstance().getMatchDataNewList(var_aio_redis)
            if len(new_match_list) <= 0:
                pass
            else:
                for var_id in new_match_list:
                    try:
                        if var_id is None:
                            #TODO log
                            continue

                        yield from flushInsertToDb(var_id.decode(),conn)

                        yield from classDataBaseMgr.getInstance().removeMatchNew(var_aio_redis, var_id)
                        logging.info("Save new match [{}]".format(var_id))
                    except Exception as e:
                        logging.error("Save new match exception, match=[{}], error=[{}]".format(var_id, str(e)))

        except Exception as e:
            logging.error(str(e))
        finally:
            pass

        # 检查更新信息
        try:
            dirty_match_list = yield from classDataBaseMgr.getInstance().getMatchDataDirtyList(var_aio_redis)
            if len(dirty_match_list) <= 0:
                pass
            else:
                for var_id in dirty_match_list:
                    try:
                        if var_id is None:
                            #TODO log
                            continue

                        yield from flushUpdateToDb(var_id.decode(),conn)

                        yield from classDataBaseMgr.getInstance().removeMatchDirty(var_aio_redis,var_id)

                        logging.info("Save dirty match [{}]".format(var_id))
                    except Exception as e:
                        logging.error("Save dirty match exception, match=[{}], error=[{}]".format(var_id, str(e)))

        except Exception as e:
            logging.error(str(e))
        finally:
            pass


@asyncio.coroutine
def flushInsertToDb(match_id: str, conn):
    objMatchrData = yield from classDataBaseMgr.getInstance().getMatchData(match_id)

    if objMatchrData is None:
        logging.error("[{}] match data not found".format(match_id))
        return

    sql = tbl.insert().values(
        matchId=objMatchrData.strMatchId,
        matchTeamALogo=objMatchrData.strTeamALogoUrl,
        teamAName=objMatchrData.strTeamAName,
        matchTeamBLogo=objMatchrData.strTeamBLogoUrl,
        teamBName=objMatchrData.strTeamBName,
        matchName=objMatchrData.strMatchName,
        #matchBO=objMatchrData.iMatchBO,
        matchState=objMatchrData.iMatchState,
        teamAScore=objMatchrData.iTeamAScore,
        teamBScore=objMatchrData.iTeamBScore,
        matchStartTime=objMatchrData.iMatchStartTimestamp,
        matchEndTime=objMatchrData.iMatchEndTimestamp,
        matchRoundNum=objMatchrData.iMatchRoundNum,
    )

    print(sql)

    #print(sql.compile().params)

    trans = yield from conn.begin()
    try:
        yield from conn.execute(sql)
    except Exception as e:

        yield from trans.rollback()
        raise e
    else:
        yield from trans.commit()


@asyncio.coroutine
def flushUpdateToDb(match_id: str, conn):
    objMatchrData = yield from classDataBaseMgr.getInstance().getMatchData(match_id)
    if objMatchrData is None:
        logging.error("[{}] match data not found".format(match_id))
        return

    sql = tbl.update().where(tbl.c.matchId == objMatchrData.strMatchId).values(
        matchId=objMatchrData.strMatchId,
        matchTeamALogo=objMatchrData.strTeamALogoUrl,
        teamAName=objMatchrData.strTeamAName,
        matchTeamBLogo=objMatchrData.strTeamBLogoUrl,
        teamBName=objMatchrData.strTeamBName,
        matchName=objMatchrData.strMatchName,
        matchState=objMatchrData.iMatchState,
        teamAScore=objMatchrData.iTeamAScore,
        teamBScore=objMatchrData.iTeamBScore,
        matchStartTime=objMatchrData.iMatchStartTimestamp,
        matchEndTime=objMatchrData.iMatchEndTimestamp,
        matchRoundNum=objMatchrData.iMatchRoundNum,
    )

    trans = yield from conn.begin()
    try:
        yield from conn.execute(sql)
    except Exception as e:

        logging.exception(e)
        yield from trans.rollback()
        raise e
    else:
        yield from trans.commit()

def getLiveMatchDataSql():
    #具体看matchstate 状态码
    #objSql = sa.select([tbl.c.matchId]).where(tbl.c.matchState > 0 and tbl.c.matchState < 4).order_by(tbl.c.matchStartTime)
    objSql = "select dj_match.matchId from dj_match where dj_match.matchState > 0 and dj_match.matchState < 4"
    return objSql

def getTodayMatchDataSql():

    #objSql = sa.select([tbl.c.matchId]).where(DATEDIFF(1,NOW())=0 and tbl.c.matchState < 4).order_by(tbl.c.matchStartTime)
    objSql = "select dj_match.matchId from dj_match where dj_match.matchStartTime > {} and  dj_match.matchStartTime < {} order by dj_match.matchStartTime".format(timeHelp.todayStartTimestamp(),timeHelp.getNow())
    return objSql

def getAllMatchDataSql():

    objSql = sa.select([tbl.c.matchId]).where(tbl.c.matchState < 4).order_by(tbl.c.matchStartTime)
    #print(objSql)
    return objSql

def getNotBeginMatchDataSql():

    objSql = sa.select([tbl.c.matchId]).where(tbl.c.matchState == 0).order_by(tbl.c.matchStartTime)
    return objSql
