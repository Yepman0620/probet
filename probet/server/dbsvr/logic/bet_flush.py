from datetime import datetime
import asyncio
import logging

from config.zoneConfig import userConfig
from datawrapper.dataBaseMgr import classDataBaseMgr


#metadata = sa.MetaData()
from lib.jsonhelp import classJsonDump

import sqlalchemy as sa

"""
import sqlalchemy as sa
tbl = sa.Table(
    'dj_bet', metadata,
    sa.Column('guessUId', sa.String(64), primary_key=True),
    sa.Column('matchId', sa.String(255), default="",nullable=False,index=True),
    sa.Column('matchType', sa.String(255), default="",nullable=False),
    sa.Column('guessId', sa.String(255), default="",nullable=False,index=True),
    sa.Column('chooseId', sa.String(255), default="",nullable=False),
    sa.Column('roundNum', sa.Integer(), default=0,nullable=False),
    sa.Column('time',  sa.Integer(), default="",nullable=False,index=True),
    sa.Column('betCoin', sa.Integer(), default=0,nullable=False),
    sa.Column('winCoin', sa.Integer(), default=0,nullable=False),
    sa.Column('result', sa.Integer(), default=0,nullable=False,index=True), #竞猜状态
    sa.Column('resultId', sa.String(255), default="",nullable=False,index=True),
    sa.Column('resultTime', sa.Integer(), default=0,nullable=False,index=True),
    sa.Column('accountId', sa.String(255), default="",nullable=False,index=True),
    sa.Column('ctr', sa.String(512), default="",nullable=False),
)
"""

from gmweb.utils.models import Base
tbl = Base.metadata.tables["dj_bet"]

@asyncio.coroutine
def doCheck():
    from datawrapper.sqlBaseMgr import classSqlBaseMgr
    engine = classSqlBaseMgr.getInstance().getEngine()
    with (yield from engine) as conn:
        # 检查写入新信息
        var_aio_redis = classDataBaseMgr.getInstance().dictAioRedis[userConfig].objAioRedis

        try:
            # 获取新生成的用户下注信息
            new_bet_list = yield from classDataBaseMgr.getInstance().getPlayerBetDataNewList(var_aio_redis)
            if len(new_bet_list) <= 0:
                pass
            else:
                for var_id in new_bet_list:
                    try:
                        if var_id is None:
                            #TODO log
                            continue
                        yield from flushInsertToDb(var_id.decode(),conn)
                        yield from classDataBaseMgr.getInstance().removePlayerBetNew(var_aio_redis, var_id)
                        logging.info("Save new playerbet [{}]".format(var_id))
                    except Exception as e:
                        logging.error("Save new playerbet exception, account=[{}], error=[{}]".format(var_id, str(e)))

        except Exception as e:
            logging.error(e)
        finally:
            pass


        # 检查更新信息
        try:
            dirty_player_list = yield from classDataBaseMgr.getInstance().getPlayerBetDataDirtyList(var_aio_redis)
            if len(dirty_player_list) <= 0:
                pass
            else:
                for var_id in dirty_player_list:
                    try:
                        if var_id is None:
                            #TODO log
                            continue

                        yield from flushUpdateToDb(var_id.decode(),conn)
                        yield from classDataBaseMgr.getInstance().removePlayerBetDirty(var_aio_redis,var_id)

                        logging.info("Save dirty user bet info[{}]".format(var_id))
                    except Exception as e:
                        logging.error("Save dirty user bet info exception, account=[{}], error=[{}]".format(var_id, str(e)))

        except Exception as e:
            logging.error(str(e))
        finally:
            pass


@asyncio.coroutine
def flushInsertToDb(history_uid:str,conn):

    objBetata = yield from classDataBaseMgr.getInstance().getBetHistory(history_uid)
    if objBetata is None:
        #TODO log
        return

    sql = tbl.insert().values(
        guessUId=objBetata.strGuessUId,
        guessName=objBetata.strGuessName,
        matchId=objBetata.strMatchId,
        matchType=objBetata.strMatchType,
        guessId=objBetata.strGuessId,
        chooseId=objBetata.strChooseId,
        roundNum=objBetata.iRoundNum,
        time=objBetata.iTime,
        betCoin=objBetata.iBetCoin,
        winCoin=objBetata.iWinCoin,
        result=objBetata.iResult,
        resultId=objBetata.strResultId,
        resultTime=objBetata.iTime if objBetata.iResultTime <= 0 else objBetata.iResultTime,
        accountId=objBetata.strAccountId,
        ctr=classJsonDump.dumps(objBetata.dictCTR),
    )




    trans = yield from conn.begin()
    try:
        yield from conn.execute(sql)
    except Exception as e:

        logging.error(e)
        yield from trans.rollback()
        raise e
    else:
        yield from trans.commit()


@asyncio.coroutine
def flushUpdateToDb(history_uid: str, conn):
    objBetata = yield from classDataBaseMgr.getInstance().getBetHistory(history_uid)
    if objBetata is None:
        # TODO log
        return

    sql = tbl.update().where(tbl.c.guessUId == objBetata.strGuessUId).values(
        guessUId=objBetata.strGuessUId,
        guessName=objBetata.strGuessName,
        matchId=objBetata.strMatchId,
        matchType=objBetata.strMatchType,
        guessId=objBetata.strGuessId,
        chooseId=objBetata.strChooseId,
        roundNum=objBetata.iRoundNum,
        time=objBetata.iTime,
        betCoin=objBetata.iBetCoin,
        winCoin=objBetata.iWinCoin,
        result=objBetata.iResult,
        resultId=objBetata.strResultId,
        resultTime=objBetata.iTime if objBetata.iResultTime <= 0 else objBetata.iResultTime,
        accountId=objBetata.strAccountId,
        ctr=classJsonDump.dumps(objBetata.dictCTR),

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
