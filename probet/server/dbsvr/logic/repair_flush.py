import asyncio
import logging
from config.zoneConfig import userConfig
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from lib.jsonhelp import classJsonDump


from gmweb.utils.models import Base
tbl = Base.metadata.tables["dj_repair"]


@asyncio.coroutine
def doCheck():
    engine = classSqlBaseMgr.getInstance().getEngine()

    with (yield from engine) as conn:
        # 检查写入信息
        var_aio_redis = classDataBaseMgr.getInstance().dictAioRedis[userConfig].objAioRedis

        try:
            new_repair_list = yield from classDataBaseMgr.getInstance().getRepairDataNewList(var_aio_redis)

            if len(new_repair_list) <= 0:
                pass
            else:
                for var_id in new_repair_list:
                    try:
                        if var_id is None:
                            logging.info(repr("无新消息"))
                            continue

                        yield from flushInsertToDb(var_id.decode(), conn)

                        yield from classDataBaseMgr.getInstance().removeRepairDataNew(var_aio_redis, var_id)

                        logging.info("Save new repair[{}]".format(var_id))
                    except Exception as e:
                        logging.error("Save new repair exception, account=[{}], error=[{}]".format(var_id, str(e)))

        except Exception as e:
            logging.error(str(e))
        finally:
            pass

        # 检查更新信息
        try:

            dirty_repair_list = yield from classDataBaseMgr.getInstance().getRepairDataDirtyList(var_aio_redis)

            if len(dirty_repair_list) <= 0:
                pass
            else:
                for var_id in dirty_repair_list:
                    try:
                        if var_id is None:
                            logging.info("Id为空")
                            continue

                        yield from flushUpdateToDb(var_id.decode(), conn)

                        yield from classDataBaseMgr.getInstance().removeRepairDataKeyDirtyList(var_aio_redis, var_id)

                        logging.info("Save dirty repair[{}]".format(var_id))
                    except Exception as e:
                        logging.error("Save dirty repair exception, account=[{}], error=[{}]".format(var_id, str(e)))

        except Exception as e:
            logging.error(str(e))
        finally:
            pass


#########################
@asyncio.coroutine
def flushInsertToDb(repairId: str, conn):
    # TODO 还需要完善dataBaseMgr中的接口

    objRepair = yield from classDataBaseMgr.getInstance().getOneRepairData(repairId)

    if objRepair is None:
        # TODO log
        return

    sql = tbl.insert().values(
        repairId=objRepair.strRepairId,
        create_time=objRepair.iTime,
        start_time=objRepair.iStartTime,
        end_time=objRepair.iEndTime,
        repairFlag=objRepair.iRepairFlag,
        accountId=objRepair.strAccountId,
        platform=objRepair.iPlatform
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
def flushUpdateToDb(repairId: str, conn):
    # TODO 还需要完善dataBaseMgr中的接口

    objRepair = yield from classDataBaseMgr.getInstance().getOneRepairData(repairId)

    if objRepair is None:
        # TODO log
        logging.info("消息为空")
        return

    sql = tbl.update().where(tbl.c.repairId == objRepair.strRepairId).values(
        repairId=objRepair.strRepairId,
        create_time=objRepair.iTime,
        start_time=objRepair.iStartTime,
        end_time=objRepair.iEndTime,
        repairFlag=objRepair.iRepairFlag,
        accountId=objRepair.strAccountId,
        platform=objRepair.iPlatform
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
