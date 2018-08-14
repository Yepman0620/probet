from datetime import datetime
import asyncio
import logging

from config.zoneConfig import userConfig, gmConfig, matchConfig
import sqlalchemy as sa
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr


metadata = sa.MetaData()

# tbl = sa.Table(
#     'dj_coin_history', metadata,
#     sa.Column('orderId', sa.String(64), primary_key=True),
#     sa.Column('orderTime', sa.Integer(), default=0,nullable=False,index=True),
#     sa.Column('coinNum', sa.Integer(), default=0,nullable=False,index=True),
#     sa.Column('tradeType', sa.Integer(), default=0,nullable=False,index=True),
#     sa.Column('tradeState', sa.Integer(), default=0,nullable=False,index=True),
#     sa.Column('accountId', sa.String(255), default="",nullable=False,index=True),
#     sa.Column('ip', sa.String(32), default="",nullable=False),
#     sa.Column('endTime', sa.Integer(), default=0,nullable=False,index=True),
#     sa.Column('transFrom', sa.String(255), default="", nullable=False),
#     sa.Column('transTo', sa.String(255), default="", nullable=False),
#     sa.Column('reviewer',sa.String(32),default="",nullable=True),
#     sa.Column('validWater',sa.Integer(),default=0,nullable=True), #有效流水，返利时用
#     sa.Column('reason',sa.String(64),default="",nullable=True),   #原因，后台补发扣款用
# )
from gmweb.utils.models import Base
tbl = Base.metadata.tables["dj_coin_history"]


@asyncio.coroutine
def doCheck():
    from datawrapper.sqlBaseMgr import classSqlBaseMgr
    engine = classSqlBaseMgr.getInstance().getEngine()
    with (yield from engine) as conn:
        # 检查写入新信息
        var_aio_redis = classDataBaseMgr.getInstance().dictAioRedis[userConfig].objAioRedis
        try:
            # 获取新生成的充值订单信息
            new_coin_history_list = yield from classDataBaseMgr.getInstance().getPlayerCoinHistoryOrderDataNewList(var_aio_redis)
            #logging.debug(new_coin_history_list)
            if len(new_coin_history_list) <= 0:
                pass
            else:
                for var_id in new_coin_history_list:
                    try:
                        if var_id is None:
                            logging.error("[{}] order id is none".format(var_id))
                            continue
                        yield from flushInsertToDb(var_id.decode(), var_aio_redis,conn)
                        yield from classDataBaseMgr.getInstance().removePlayerCoinHistoryOrderNew(var_aio_redis, var_id)
                        logging.info("Save new coin history [{}]".format(var_id))
                    except Exception as e:
                        logging.error("Save new coin history exception order id=[{}], error=[{}]".format(var_id,str(e)))

            dirty_coin_history_list = yield from classDataBaseMgr.getInstance().getPlayerCoinHistoryOrderDataDirtyList(
                var_aio_redis)
            # logging.debug(new_coin_history_list)
            if len(dirty_coin_history_list) <= 0:
                pass
            else:
                for var_id in dirty_coin_history_list:
                    try:
                        if var_id is None:
                            logging.error("[{}] order id is none".format(var_id))
                            continue
                        yield from flushUpdateToDb(var_id.decode(), var_aio_redis, conn)
                        yield from classDataBaseMgr.getInstance().removePlayerCoinHistoryOrderDirty(var_aio_redis, var_id)
                        logging.info("Save dirty coin history [{}]".format(var_id))
                    except Exception as e:
                        logging.error(
                            "Save dirty coin history exception order id=[{}], error=[{}]".format(var_id, str(e)))

        except Exception as e:
            logging.error(str(e))
        finally:
            pass

@asyncio.coroutine
def flushInsertToDb(order_id:str, redisPool,conn):

    objOrderData = yield from classDataBaseMgr.getInstance().getCoinHis(order_id, redisPool)
    if objOrderData is None:
        #TODO log
        return

    sql = tbl.insert().values(
        orderId=objOrderData.strOrderId,
        orderTime=objOrderData.iTime,
        coinNum=objOrderData.iCoin,
        balance=objOrderData.iBalance,
        tradeType=objOrderData.iTradeType,
        tradeState=objOrderData.iTradeState,
        accountId=objOrderData.strAccountId,
        ip=objOrderData.strIp,
        endTime=objOrderData.iEndTime,
        transFrom=objOrderData.strTransFrom,
        transTo=objOrderData.strTransTo,
        reviewer=objOrderData.strReviewer,
        validWater=objOrderData.iValidWater,
        reason=objOrderData.strReason,
        bankOrderId=objOrderData.strBankOrderId,
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
def flushUpdateToDb(order_id, redisPool,conn):
    objOrderData = yield from classDataBaseMgr.getInstance().getCoinHis(order_id, redisPool)
    if objOrderData is None:
        # TODO log
        return

    sql = tbl.update().where(tbl.c.orderId == objOrderData.strOrderId).values(
        orderId=objOrderData.strOrderId,
        orderTime=objOrderData.iTime,
        coinNum=objOrderData.iCoin,
        balance=objOrderData.iBalance,
        tradeType=objOrderData.iTradeType,
        tradeState=objOrderData.iTradeState,
        accountId=objOrderData.strAccountId,
        ip=objOrderData.strIp,
        endTime=objOrderData.iEndTime,
        transFrom=objOrderData.strTransFrom,
        transTo=objOrderData.strTransTo,
        reviewer=objOrderData.strReviewer,
        validWater=objOrderData.iValidWater,
        reason=objOrderData.strReason,
        bankOrderId=objOrderData.strBankOrderId,
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
