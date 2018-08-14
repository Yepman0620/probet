import asyncio
import logging

from config.zoneConfig import matchConfig
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr

from gmweb.utils.models import Base
tbl = Base.metadata.tables["dj_match_guess"]

@asyncio.coroutine
def flushInsertToDb(match_guess_id:str,conn):
    objMatchGuessData = yield from classDataBaseMgr.getInstance().getGuessData(match_guess_id)
    if objMatchGuessData is None:
        #TODO log
        return
    sql = tbl.insert().values(
        guessId=objMatchGuessData.strGuessId,
        guessName=objMatchGuessData.strGuessName,
        guessState=objMatchGuessData.iGuessState,
        #matchId=objMatchGuessData.strMatchId,
        hideFlag=objMatchGuessData.iHideFlag,
        limitPerAccount=objMatchGuessData.iLimitPerAccount,
        ownerMatchId=objMatchGuessData.strOwnerMatchId,
        roundNum=objMatchGuessData.iRoundNum,
        cancelResultFlag=objMatchGuessData.iCancelResultFlag,
        cancelResultBeginTime=objMatchGuessData.iCancelResultBeginTime,
        cancelResultEndTime=objMatchGuessData.iCancelResultEndTime,
        ctr=classJsonDump.dumps(objMatchGuessData.dictCTR),
    )

    #print(sql)

    #print(sql.compile().params)

    trans = yield from conn.begin()
    try:
        yield from conn.execute(sql)
    except Exception as e:
        #print("flushInsertToDb match_guess Exception ---->", e)
        logging.error("flushInsertToDb match_guess Exception ---->{} ", repr(e))

        yield from trans.rollback()
        raise e
    else:
        yield from trans.commit()


@asyncio.coroutine
def doCheck():
    from datawrapper.sqlBaseMgr import classSqlBaseMgr
    engine = classSqlBaseMgr.getInstance().getEngine()
    with (yield from engine) as conn:
        # 检查写入新信息
        var_aio_redis = classDataBaseMgr.getInstance().dictAioRedis[matchConfig].objAioRedis
        try:
            new_guess_list = yield from classDataBaseMgr.getInstance().getMatchGuessDataNewList(var_aio_redis)
            if len(new_guess_list) <= 0:
                pass
            else:
                for var_id in new_guess_list:
                    try:
                        if var_id is None:
                            #TODO log
                            continue

                        yield from flushInsertToDb(var_id.decode(),conn)

                        yield from classDataBaseMgr.getInstance().removeMatchGuessNew(var_aio_redis, var_id)
                        logging.info("Save new matchguess[{}]".format(var_id))
                    except Exception as e:
                        logging.error("Save new matchguess exception, guess=[{}], error=[{}]".format(var_id, str(e)))
        except Exception as e:
            logging.error(str(e))
        finally:
            pass

        # 检查更新信息
        try:
            dirty_guess_list = yield from classDataBaseMgr.getInstance().getMatchGuessDataDirtyList(var_aio_redis)
            if len(dirty_guess_list) <= 0:
                pass
            else:
                for var_id in dirty_guess_list:
                    try:
                        if var_id is None:
                            #TODO log
                            continue

                        yield from flushUpdateToDb(var_id.decode(),conn)

                        yield from classDataBaseMgr.getInstance().removeMatchGuessDirty(var_aio_redis,var_id)

                        logging.info("Save dirty matchguess[{}]".format(var_id))
                    except Exception as e:
                        logging.error("Save dirty matchguess exception, guess=[{}], error=[{}]".format(var_id, str(e)))

        except Exception as e:
            logging.error(str(e))
        finally:
            pass


@asyncio.coroutine
def flushUpdateToDb(guess_id: str, conn):
    objMatchGuessData = yield from classDataBaseMgr.getInstance().getGuessData(guess_id)
    if objMatchGuessData is None:
        # TODO log
        return

    sql = tbl.update().where(tbl.c.guessId == objMatchGuessData.strGuessId).values(
        guessId=objMatchGuessData.strGuessId,
        guessName=objMatchGuessData.strGuessName,
        guessState=objMatchGuessData.iGuessState,
        #matchId=objMatchGuessData.strMatchId,
        hideFlag=objMatchGuessData.iHideFlag,
        limitPerAccount=objMatchGuessData.iLimitPerAccount,
        ownerMatchId=objMatchGuessData.strOwnerMatchId,
        roundNum=objMatchGuessData.iRoundNum,
        cancelResultFlag=objMatchGuessData.iCancelResultFlag,
        cancelResultBeginTime=objMatchGuessData.iCancelResultBeginTime,
        cancelResultEndTime=objMatchGuessData.iCancelResultEndTime,
        ctr=classJsonDump.dumps(objMatchGuessData.dictCTR),
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

    return True