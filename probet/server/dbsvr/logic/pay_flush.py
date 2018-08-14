from datetime import datetime
import asyncio
import logging
import sqlalchemy as sa
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr
from config.zoneConfig import miscConfig


from gmweb.utils.models import Base
tbl = Base.metadata.tables["dj_pay_order"]

@asyncio.coroutine
def doCheck():

    engine = classSqlBaseMgr.getInstance().getEngine()

    with (yield from engine) as conn:
        # 检查写入新信息
        var_aio_redis = classDataBaseMgr.getInstance().dictAioRedis[miscConfig].objAioRedis
        # 获取新生成的充值订单信息
        new_bet_map = yield from classDataBaseMgr.getInstance().getPayOrderDataNewList(var_aio_redis)
        if len(new_bet_map) <= 0:
            pass
        else:
            for var_key in new_bet_map:
                try:

                    yield from flushInsertToDb(var_key.decode(),conn)
                    yield from classDataBaseMgr.getInstance().removePayOrderNew(var_aio_redis, var_key)
                    logging.info("Save new pay order  [{}]".format(var_key))

                except Exception as e:
                    logging.error("Save new pay order exception, orderId=[{}], error=[{}]".format(var_key, str(e)))

        # 获取要更新的充值订单信息
        dirty_bet_map = yield from classDataBaseMgr.getInstance().getPayOrderDataDirtyList(var_aio_redis)
        if len(dirty_bet_map) <= 0:
            pass
        else:
            for var_key in dirty_bet_map:
                try:

                    yield from flushUpdateToDb(var_key.decode(), conn)
                    yield from classDataBaseMgr.getInstance().removePayOrderDirty(var_aio_redis, var_key)
                    logging.info("Save dirty pay order  [{}]".format(var_key))

                except Exception as e:
                    logging.error("Save dirty pay order exception, orderId=[{}], error=[{}]".format(var_key, str(e)))


@asyncio.coroutine
def flushInsertToDb(order_id:str,conn):
    objOrderData = yield from classDataBaseMgr.getInstance().getPayOrder(order_id)
    if objOrderData is None:
        logging.error("[{}] is None".format(order_id))
        return

    sql = tbl.insert().values(
        payOrder=objOrderData.strPayOrder,
        thirdPayOrder=objOrderData.strThirdPayOrder,
        thirdPayName=objOrderData.strThirdPayName,
        payChannel=objOrderData.strPayChannel,
        accountId=objOrderData.strAccountId,
        orderTime=objOrderData.iOrderTime,
        buyCoin=objOrderData.iBuyCoin,
        payTime=objOrderData.iPayTime,
        ip=objOrderData.strIp,
        bank=objOrderData.strBank,
        status=objOrderData.iStatus,
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
def flushUpdateToDb(order_id:str, conn):

    objOrderData = yield from classDataBaseMgr.getInstance().getPayOrder(order_id)
    if objOrderData is None:
        logging.error("[{}] is None".format(order_id))
        return

    sql = tbl.update().where(tbl.c.payOrder == objOrderData.strPayOrder).values(
        thirdPayOrder=objOrderData.strThirdPayOrder,
        thirdPayName=objOrderData.strThirdPayName,
        payChannel=objOrderData.strPayChannel,
        accountId=objOrderData.strAccountId,
        orderTime=objOrderData.iOrderTime,
        buyCoin=objOrderData.iBuyCoin,
        payTime=objOrderData.iPayTime,
        ip=objOrderData.strIp,
        bank=objOrderData.strBank,
        status=objOrderData.iStatus,
    )

    #rint(sql)

    #print(sql.compile().params)

    trans = yield from conn.begin()
    try:
        yield from conn.execute(sql)
    except Exception as e:

        logging.error(e)
        yield from trans.rollback()
        raise e
    else:
        yield from trans.commit()
