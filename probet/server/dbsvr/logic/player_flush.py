import json
import asyncio
import logging

from config.zoneConfig import userConfig
#Base = declarative_base()
from datawrapper.dataBaseMgr import classDataBaseMgr



from gmweb.utils.models import Base
tbl = Base.metadata.tables["dj_account"]


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

            new_player_list = yield from classDataBaseMgr.getInstance().getAccountDataNewList(var_aio_redis)
            if len(new_player_list) <= 0:
                pass
            else:

                for var_id in new_player_list:
                    try:
                        if var_id is None:
                            #TODO log
                            continue

                        yield from flushInsertToDb(var_id.decode(),conn)

                        #listSaved.append(var_id)
                        yield from classDataBaseMgr.getInstance().removeNew(var_aio_redis, var_id)
                        logging.info("Save new player[{}]".format(var_id))
                    except Exception as e:
                        logging.error("Save new player exception, account=[{}], error=[{}]".format(var_id, str(e)))

        except Exception as e:
            logging.error(str(e))
        finally:
            pass
            #if listSaved.__len__() > 0:
            #    yield from classDataBaseMgr.getInstance().removeNewList(listSaved)

        try:

            dirty_player_list = yield from classDataBaseMgr.getInstance().getAccountDataDirtyList(var_aio_redis)
            if len(dirty_player_list) <= 0:
                pass
            else:


                for var_id in dirty_player_list:
                    try:
                        if var_id is None:
                            #TODO log
                            continue

                        yield from flushUpdateToDb(var_id.decode(),conn)

                        #listSaved.append(var_id)
                        yield from classDataBaseMgr.getInstance().removeDirty(var_aio_redis,var_id)

                        logging.info("Save dirty player[{}]".format(var_id))
                    except Exception as e:
                        logging.error("Save dirty player exception, account=[{}], error=[{}]".format(var_id, str(e)))

        except Exception as e:
            logging.error(str(e))
        finally:
            pass


@asyncio.coroutine
def flushInsertToDb(account_id:str,conn):

    objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(account_id)
    if objPlayerData is None:
        #TODO log
        return


    sql=tbl.insert().values(
        accountId=objPlayerData.strAccountId,
        userType=objPlayerData.iUserType,
        phone=objPlayerData.strPhone,
        coin=objPlayerData.iCoin,
        guessCoin=objPlayerData.iGuessCoin,
        pingboCoin=objPlayerData.iPingboCoin,
        notDrawingCoin=objPlayerData.iNotDrawingCoin,
        passwordMd5=objPlayerData.strPassword,
        regTime=objPlayerData.iRegTime,
        email=objPlayerData.strEmail,

        loginTime=objPlayerData.iLastLoginTime,
        loginIp=objPlayerData.strLastLoginIp,
        loginDeviceUdid=objPlayerData.strLastLoginUdid,
        loginDeviceModel=objPlayerData.strLastDeviceModal,
        loginDeviceName=objPlayerData.strLastDeviceName,
        lastBetTime=objPlayerData.iLastBetTime,
        platform=objPlayerData.iPlatform,
        # lastReceviveMsgTime=objPlayerData.iLastReceiveMsgTime,
        headAddress=objPlayerData.strHeadAddress,
        realName=objPlayerData.strRealName,
        sex=objPlayerData.strSex,
        born=objPlayerData.strBorn,
        address=json.dumps(objPlayerData.dictAddress),
        bankcard=json.dumps(objPlayerData.arrayBankCard),
        tradePasswordMd5=objPlayerData.strTradePassword,
        level=objPlayerData.iLevel,
        levelValidWater=objPlayerData.iLevelValidWater,
        status=objPlayerData.iStatus,
        lockEndTime=objPlayerData.iLockEndTime,
        lockStartTime=objPlayerData.iLockStartTime,
        lockReason=objPlayerData.strLockReason,
        logoutTime=objPlayerData.iLogoutTime,
        loginAddress=objPlayerData.strLoginAddress,
        #lastPayTime=objPlayerData.iLastPayTime,
        firstPayCoin=objPlayerData.iFirstPayCoin,
        firstPayTime=objPlayerData.iFirstPayTime,
        #MBWater=objPlayerData.iMBWater,
        #MBWaterTime=objPlayerData.iMBWaterTime,
        agentId=objPlayerData.strAgentId,
        lastPBCRefreshTime=objPlayerData.iLastPBCRefreshTime,
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
def flushUpdateToDb(account_id: str, conn):
    objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(account_id)
    if objPlayerData is None:
        # TODO log
        logging.info("用户为空")
        return

    sql=tbl.update().where(tbl.c.accountId==objPlayerData.strAccountId).values(
        accountId=objPlayerData.strAccountId,
        userType=objPlayerData.iUserType,
        phone=objPlayerData.strPhone,
        coin=objPlayerData.iCoin,
        guessCoin=objPlayerData.iGuessCoin,
        pingboCoin=objPlayerData.iPingboCoin,
        notDrawingCoin=objPlayerData.iNotDrawingCoin,
        passwordMd5=objPlayerData.strPassword,
        regTime=objPlayerData.iRegTime,
        email=objPlayerData.strEmail,
        loginTime=objPlayerData.iLastLoginTime,
        loginIp=objPlayerData.strLastLoginIp,
        loginDeviceUdid=objPlayerData.strLastLoginUdid,
        levelValidWater=objPlayerData.iLevelValidWater,
        loginDeviceModel=objPlayerData.strLastDeviceModal,
        loginDeviceName=objPlayerData.strLastDeviceName,
        lastBetTime=objPlayerData.iLastBetTime,
        platform=objPlayerData.iPlatform,
        firstPayCoin=objPlayerData.iFirstPayCoin,
        firstPayTime=objPlayerData.iFirstPayTime,
        # lastReceviveMsgTime=objPlayerData.iLastReceiveMsgTime,
        headAddress=objPlayerData.strHeadAddress,
        realName=objPlayerData.strRealName,
        sex=objPlayerData.strSex,
        born=objPlayerData.strBorn,
        address=json.dumps(objPlayerData.dictAddress),
        bankcard=json.dumps(objPlayerData.arrayBankCard),
        tradePasswordMd5=objPlayerData.strTradePassword,
        status=objPlayerData.iStatus,
        level=objPlayerData.iLevel,
        lockReason=objPlayerData.strLockReason,
        lockEndTime=objPlayerData.iLockEndTime,
        lockStartTime=objPlayerData.iLockStartTime,
        logoutTime=objPlayerData.iLogoutTime,
        loginAddress=objPlayerData.strLoginAddress,
        agentId=objPlayerData.strAgentId,
        lastPBCRefreshTime=objPlayerData.iLastPBCRefreshTime,
    )
    trans=yield from conn.begin()
    try:
        yield from conn.execute(sql)
    except Exception as e :
        logging.exception(e)
        yield from trans.rollback()
        raise e
    else:
        yield from trans.commit()
