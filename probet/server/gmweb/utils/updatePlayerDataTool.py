import asyncio
import sys
import os
from datawrapper.dataBaseMgr import classDataBaseMgr
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")
import signal
from optparse import OptionParser
from config.zoneConfig import *

g_obj_loop = asyncio.get_event_loop()
g_debug = False
g_obj_dataMgr = None


redis_config = {

    miscConfig:{
        'address':redis_address_for_misc,
        'hashRing':0,
        'dbIndex':redis_misc_db,
        'pwd':redis_pwd,
    },

    userConfig:{
        'address':redis_address_list_for_user,
        'hashRing':1,
        'dbIndex':redis_user_data_db,
        'pwd':redis_pwd,
    },
    matchConfig:{
        'address':redis_address_for_match,
        'hashRing':0,
        'dbIndex':redis_match_data_db,
        'pwd':redis_pwd,
    },

}


redis_config_debug = {

    miscConfig:{
        'address':redis_debug_address_for_misc,
        'hashRing':0,
        'dbIndex':redis_misc_db,
        'pwd':redis_pwd,
    },

    userConfig:{
        'address':redis_debug_address_list_for_user,
        'hashRing':1,
        'dbIndex':redis_match_data_db,
        'pwd':redis_pwd,
    },

    matchConfig:{
        'address':redis_debug_address_for_match,
        'hashRing':0,
        'dbIndex':redis_match_data_db,
        'pwd':redis_pwd,
    },
}



def __stopServer():
    pass


def call(account_id):

    global g_obj_dataMgr
    #修改redis数据
    objPlayerData, objLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(account_id)
    with (yield from g_obj_dataMgr.dictAioRedis[userConfig].getRedisPoolByKey(account_id)) as redis:
        pass


    g_obj_loop.stop()


def init():
    #init redis
    global g_obj_dataMgr

    if g_debug:
        g_obj_dataMgr=classDataBaseMgr(
            redis_config_debug, g_obj_loop, g_debug, 1, 1)
    else:
        g_obj_dataMgr = classDataBaseMgr(redis_config, g_obj_loop, g_debug, 1, 1)

    yield from g_obj_dataMgr.getInstance().connectRedis()
    yield from g_obj_dataMgr.getInstance().loadRedisLuaScript()

    #call
    g_obj_loop.call_later(2, lambda: asyncio.async(call(account_id=1)))


if __name__ == "__main__":

    if sys.version_info[0] < 3:
        print("Found Python interpreter less 3.0 version not support: %s \n"%sys.version)
        sys.exit()
    else:
        parser = OptionParser(usage="%prog --rf <runFlag> ", version="%prog 0.3")
        parser.add_option("--rf", "--runFlag", dest="runFlag", help="runFlag debug or release")


        (options, args) = parser.parse_args()
        runFlag = str(options.runFlag)
        if runFlag == "debug":
            g_debug = True

    # register the signal stop the loop
    stop = asyncio.Future()
    g_obj_loop.add_signal_handler(signal.SIGUSR1, stop.set_result, None)
    signal.signal(signal.SIGUSR1, __stopServer)
    try:
        asyncio.async(init())

        g_obj_loop.run_forever()
    except KeyboardInterrupt as e:
        print(asyncio.Task.all_tasks())
        print(asyncio.gather(*asyncio.Task.all_tasks()).cancel())
        g_obj_loop.stop()
        g_obj_loop.run_forever()
    except:
        #logging.error(traceback.format_exc())
        exit(0)
    finally:
        g_obj_loop.close()