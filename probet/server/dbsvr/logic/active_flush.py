import json
import asyncio
import logging
from lib.jsonhelp import classJsonDump
from config.zoneConfig import userConfig
#Base = declarative_base()
from datawrapper.dataBaseMgr import classDataBaseMgr

from gmweb.utils.models import Base
tbl = Base.metadata.tables["dj_active"]


@asyncio.coroutine
def doCheck():
    from datawrapper.sqlBaseMgr import classSqlBaseMgr
    engine = classSqlBaseMgr.getInstance().getEngine()

    with (yield from engine) as conn:
        #检查写入新信息
        var_aio_redis = classDataBaseMgr.getInstance().dictAioRedis[userConfig].objAioRedis
        #print(var_key)
        #listSaved = []
        try:

            new_task_list = yield from classDataBaseMgr.getInstance().getActiveDataNewList(var_aio_redis)
            if len(new_task_list) <= 0:
                pass
            else:

                for var_id in new_task_list:
                    try:
                        if var_id is None:
                            #TODO log
                            continue

                        yield from flushInsertToDb(var_id.decode(),conn)

                        #listSaved.append(var_id)
                        yield from classDataBaseMgr.getInstance().removeNewActiveList(var_aio_redis, var_id)
                        logging.info("Save new active[{}]".format(var_id))
                    except Exception as e:
                        logging.error("Save new active exception, active=[{}], error=[{}]".format(var_id, str(e)))

        except Exception as e:
            logging.error(str(e))
        finally:
            pass
            #if listSaved.__len__() > 0:
            #    yield from classDataBaseMgr.getInstance().removeNewList(listSaved)

        try:

            dirty_active_list = yield from classDataBaseMgr.getInstance().getActiveDataDirtyList(var_aio_redis)
            if len(dirty_active_list) <= 0:
                pass
            else:
                for var_id in dirty_active_list:
                    try:
                        if var_id is None:
                            #TODO log
                            continue

                        yield from flushUpdateToDb(var_id.decode(),conn)

                        #listSaved.append(var_id)
                        yield from classDataBaseMgr.getInstance().removeActiveDirtyList(var_aio_redis,var_id)

                        logging.info("Save dirty active[{}]".format(var_id))
                    except Exception as e:
                        logging.error("Save dirty active exception, active=[{}], error=[{}]".format(var_id, str(e)))

        except Exception as e:
            logging.error(str(e))
        finally:
            pass


@asyncio.coroutine
def flushInsertToDb(accountId:str,conn):

    objActiveData = yield from classDataBaseMgr.getInstance().getActiveData(accountId)
    if objActiveData is None:
        #TODO log
        return


    sql=tbl.insert().values(
        accountId=objActiveData.strAccountId,
        dictActiveItem=classJsonDump.dumps(objActiveData.dictActiveItem).decode(),
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
def flushUpdateToDb(accountId: str, conn):

    objActiveData = yield from classDataBaseMgr.getInstance().getActiveData(accountId)
    if objActiveData is None:
        # TODO log
        return

    sql = tbl.update().where(tbl.c.accountId==objActiveData.strAccountId).values(
        accountId=objActiveData.strAccountId,
        dictActiveItem=classJsonDump.dumps(objActiveData.dictActiveItem).decode(),
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