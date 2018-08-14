import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")
from lib.signalprocesslog import singlePLogger as log
from dbsvr.proc import procVariable
from optparse import OptionParser
from dbsvr.logic import player_flush, match_flush, guess_flush, bet_flush, user_coin_history_flush,all_msg_flush,pay_flush,repair_flush,commission_data_flush,active_flush,pingbo_coin_flush
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from dbsvr import db_config
import logging
import asyncio
import signal
import os
import uvloop

g_updata_count = 0
g_obj_loop = asyncio.get_event_loop()

def __stopServer():
    pass

def __initLog():
    log.initLogger(os.path.dirname(os.path.realpath(__file__)) + "/../logdata/", "db_svr",logging.NOTSET)

@asyncio.coroutine
def __update():

    global g_updata_count


    try:
        yield from player_flush.doCheck()
        yield from match_flush.doCheck()
        yield from guess_flush.doCheck()
        yield from bet_flush.doCheck()

        yield from user_coin_history_flush.doCheck()
        yield from pay_flush.doCheck()
        yield from repair_flush.doCheck()
        yield from active_flush.doCheck()
        yield from commission_data_flush.doCheck()
        yield from pingbo_coin_flush.doCheck()
        # 为了能每过5秒后执行这个函数时，同时检查4中消息有没有入库
        iterDoCheck=map(all_msg_flush.doCheck,[x for x in range(4)])
        for var_check in iterDoCheck:
            yield from var_check
        #yield from user_coin_history_flush.doCheck()    # 用户金币消耗/增加 账单

        g_updata_count += 1
        if g_updata_count >= 10:
            logging.info("update call [{}]".format(g_updata_count))
            g_updata_count = 0

    except Exception as e:
        logging.error(e)

    g_obj_loop.call_later(1, lambda: asyncio.async(__update()))

@asyncio.coroutine
def __initData():

    if procVariable.debug:
        classDataBaseMgr(db_config.redis_config_debug,g_obj_loop,procVariable.debug,  2, 2)
    else:
        classDataBaseMgr(db_config.redis_config,g_obj_loop,procVariable.debug)

    yield from classDataBaseMgr.getInstance().connectRedis()
    yield from classDataBaseMgr.getInstance().loadRedisLuaScript()

    classSqlBaseMgr()

    if procVariable.debug:
        yield from classSqlBaseMgr.getInstance().connetSql(db_config.mysqlAddress_debug, 3306,
                                                           'root', db_config.mysqlPwd_debug, 'probet_data',
                                                           g_obj_loop)
    else:
        yield from classSqlBaseMgr.getInstance().connetSql(db_config.mysqlAddress, 3306,
                                                           'root', db_config.mysqlPwd, 'probet_data',
                                                           g_obj_loop)


@asyncio.coroutine
def init():
    try:
        g_obj_loop.set_debug(procVariable.debug)
        logging.getLogger('asyncio').setLevel(db_config.async_log_level)
        logging.getLogger('aioredis').setLevel(db_config.redis_log_level)

        __initLog()

        yield from __initData()

        g_obj_loop.call_later(5, lambda: asyncio.async(__update()))

        sys.stdout.write("-----> All modules start up successfully! <-----")
        sys.stdout.flush()

    except Exception as e:
        exit(0)


if __name__ == "__main__":

    if sys.version_info[0] < 3:
        print("Found Python interpreter less 3.0 version not support: %s \n" % sys.version)
        sys.exit()
    else:
        parser = OptionParser(usage="%prog --rf <runFlag>",
                              version="%prog 0.3")
        parser.add_option("--rf", "--runFlag", dest="runFlag", help="runFlag debug or release")
        parser.add_option("--gdb", "--gdb", dest="gdb", help="gdb")


        (options, args) = parser.parse_args()

        runFlag = str(options.runFlag)
        gdb = str(options.gdb)

        if runFlag == "gdb":
            procVariable.gdb = True

        if runFlag == "debug":
            procVariable.debug = True

        elif runFlag == "release":
            procVariable.debug = False
            if not procVariable.gdb:
                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
                g_obj_loop = asyncio.get_event_loop()

        else:
            print("runFlag is not valid please --help the detail")
            exit(0)


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