import json
import asyncio
import logging

from config.zoneConfig import userConfig
#Base = declarative_base()
from datawrapper.dataBaseMgr import classDataBaseMgr
from gmweb.handle.pinbo.get_player_info import get_pingbo_player_info

from gmweb.utils.models import Base
tbl = Base.metadata.tables["dj_account"]


@asyncio.coroutine
def doCheck():
    #检查写入新信息
    var_aio_redis = classDataBaseMgr.getInstance().dictAioRedis[userConfig].objAioRedis
    try:
        accountId = yield from classDataBaseMgr.getInstance().getUpdatePingboAccountId(var_aio_redis)
        if accountId is None:
            pass
        else:
            accountId=accountId.decode()
            objPlayerData ,objLock= yield from classDataBaseMgr.getInstance().getPlayerDataByLock(accountId)
            if objPlayerData is None:
                # TODO log
                logging.info("用户为空")
                return
            pingbo_info = yield from get_pingbo_player_info(accountId)
            objPlayerData.iPingboCoin=pingbo_info['availableBalance']*100
            yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData,objLock)
            logging.info("update player[{}] pingboCoin".format(accountId))
    except Exception as e:
        logging.error(str(e))
        yield from classDataBaseMgr.getInstance().releasePlayerDataLock(accountId,objLock)
