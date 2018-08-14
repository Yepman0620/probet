from datetime import datetime
import asyncio
import logging

from config.zoneConfig import userConfig, gmConfig, matchConfig
import sqlalchemy as sa
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from datawrapper.dataBaseMgr import classDataBaseMgr


metadata = sa.MetaData()

from gmweb.utils.models import Base
tbl = Base.metadata.tables["dj_agent_commission"]


@asyncio.coroutine
def doCheck():
    from datawrapper.sqlBaseMgr import classSqlBaseMgr
    engine = classSqlBaseMgr.getInstance().getEngine()
    with (yield from engine) as conn:
        # 检查写入新信息
        var_aio_redis = classDataBaseMgr.getInstance().dictAioRedis[userConfig].objAioRedis
        try:
            # 获取新生成的佣金账单信息
            new_commission_bill_list = yield from classDataBaseMgr.getInstance().getAgentCommissionDataNewList(var_aio_redis)
            #logging.debug(new_coin_history_list)
            if len(new_commission_bill_list) <= 0:
                pass
            else:
                for var_id in new_commission_bill_list:
                    try:
                        if var_id is None:
                            logging.error("[{}] bill id is none".format(var_id))
                            continue
                        yield from flushInsertToDb(var_id.decode(), var_aio_redis,conn)
                        yield from classDataBaseMgr.getInstance().removeAgentCommissionDataNew(var_aio_redis, var_id)
                        logging.info("Save new commission bill [{}]".format(var_id))
                    except Exception as e:
                        logging.error("Save new commission bill exception bill id=[{}], error=[{}]".format(var_id,str(e)))

            dirty_commission_bill_list = yield from classDataBaseMgr.getInstance().getAgentCommissionDataDirtyList(
                var_aio_redis)
            # logging.debug(new_coin_history_list)
            if len(dirty_commission_bill_list) <= 0:
                pass
            else:
                for var_id in dirty_commission_bill_list:
                    try:
                        if var_id is None:
                            logging.error("[{}] order id is none".format(var_id))
                            continue
                        yield from flushUpdateToDb(var_id.decode(), var_aio_redis, conn)
                        yield from classDataBaseMgr.getInstance().removeAgentCommissionDataDirty(var_aio_redis, var_id)
                        logging.info("Save dirty commission bill [{}]".format(var_id))
                    except Exception as e:
                        logging.error(
                            "Save dirty commission bill exception order id=[{}], error=[{}]".format(var_id, str(e)))

        except Exception as e:
            logging.error(str(e))
        finally:
            pass

@asyncio.coroutine
def flushInsertToDb(billId:str, redisPool,conn):

    objCommissionData = yield from classDataBaseMgr.getInstance().getAgentCommissionData(billId, redisPool)
    if objCommissionData is None:
        #TODO log
        return

    sql = tbl.insert().values(
        billId=objCommissionData.strBillId,
        billTime=objCommissionData.iTime,
        agentId=objCommissionData.strAgentId,
        dateYear=objCommissionData.iYear,
        dateMonth=objCommissionData.iMonth,
        newAccount=objCommissionData.iNewAccount,
        activeAccount=objCommissionData.iActiveAccount,
        probetWinLoss=objCommissionData.iProbetWinLoss,
        pingboWinLoss=objCommissionData.iPingboWinLoss,
        winLoss=objCommissionData.iWinLoss,
        probetRate=objCommissionData.fProbetRate,
        pingboRate=objCommissionData.fPingboRate,
        probetCost=objCommissionData.iProbetCost,
        pingboCost=objCommissionData.iPingboCost,
        platformCost=objCommissionData.iPlatformCost,
        depositDrawingCost=objCommissionData.iDepositDrawingCost,
        backWater=objCommissionData.iBackWater,
        bonus=objCommissionData.iBonus,
        water=objCommissionData.iWater,
        netProfit=objCommissionData.iNetProfit,
        preBalance=objCommissionData.iPreBalance,
        balance=objCommissionData.iBalance,
        commissionRate=objCommissionData.fCommissionRate,
        commission=objCommissionData.iCommission,
        status=objCommissionData.iStatus,
        reviewer=objCommissionData.strReviewer,
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
def flushUpdateToDb(billId, redisPool,conn):
    objCommissionData = yield from classDataBaseMgr.getInstance().getAgentCommissionData(billId, redisPool)
    if objCommissionData is None:
        # TODO log
        return

    sql = tbl.update().where(tbl.c.billId == objCommissionData.strBillId).values(
        billId=objCommissionData.strBillId,
        billTime=objCommissionData.iTime,
        agentId=objCommissionData.strAgentId,
        dateYear=objCommissionData.iYear,
        dateMonth=objCommissionData.iMonth,
        newAccount=objCommissionData.iNewAccount,
        activeAccount=objCommissionData.iActiveAccount,
        probetWinLoss=objCommissionData.iProbetWinLoss,
        pingboWinLoss=objCommissionData.iPingboWinLoss,
        winLoss=objCommissionData.iWinLoss,
        probetRate=objCommissionData.fProbetRate,
        pingboRate=objCommissionData.fPingboRate,
        probetCost=objCommissionData.iProbetCost,
        pingboCost=objCommissionData.iPingboCost,
        platformCost=objCommissionData.iPlatformCost,
        depositDrawingCost=objCommissionData.iDepositDrawingCost,
        backWater=objCommissionData.iBackWater,
        bonus=objCommissionData.iBonus,
        water=objCommissionData.iWater,
        netProfit=objCommissionData.iNetProfit,
        preBalance=objCommissionData.iPreBalance,
        balance=objCommissionData.iBalance,
        commissionRate=objCommissionData.fCommissionRate,
        commission=objCommissionData.iCommission,
        status=objCommissionData.iStatus,
        reviewer=objCommissionData.strReviewer,
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
