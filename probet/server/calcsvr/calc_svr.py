import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")
import logging
from lib.signalprocesslog import singlePLogger as log
from optparse import  OptionParser
from calcsvr.proc import procVariable
from calcsvr import calc_config
from calcsvr.logic import waterCalc
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
import uvloop
import signal
import asyncio

g_updata_count = 0
g_obj_loop = asyncio.get_event_loop()


def __stopServer():
    pass


@asyncio.coroutine
def __secTickCallLater():
    global g_updata_count

    try:
        yield from waterCalc.calcDayWater()
        yield from waterCalc.calcMonthVip()
        yield from waterCalc.calcMonthCommission()
        #yield from waterCalc.calcMonthForNowCommission()

        g_updata_count += 1
        if g_updata_count >= 10:
            logging.info("update call [{}]".format(g_updata_count))
            g_updata_count = 0
    except Exception as e:
        logging.error(e)

    g_obj_loop.call_later(1, lambda: asyncio.async(__secTickCallLater()))
    logging.info("ticket the service")


def __initLog():
    log.initLogger(os.path.dirname(os.path.realpath(__file__)) + "/../logdata/", "calc_svr",
                   calc_config.log_level, procVariable.debug)




@asyncio.coroutine
def __initLogicDataMgr():
    if procVariable.debug:
        classDataBaseMgr(calc_config.redis_config_debug, g_obj_loop,procVariable.debug,  1, 1)
    else:
        classDataBaseMgr(calc_config.redis_config, g_obj_loop,procVariable.debug, 1,1)

    yield from classDataBaseMgr.getInstance().connectRedis()
    yield from classDataBaseMgr.getInstance().loadRedisLuaScript()

    classSqlBaseMgr()

    if procVariable.debug:
        yield from classSqlBaseMgr.getInstance().connetSql(calc_config.mysqlAddress_debug, 3306,
                                                           'root', calc_config.mysqlPwd_debug, 'probet_data',
                                                           g_obj_loop)

    else:
        yield from classSqlBaseMgr.getInstance().connetSql(calc_config.mysqlAddress, 3306,
                                                           'root', calc_config.mysqlPwd, 'probet_data',
                                                           g_obj_loop)


@asyncio.coroutine
def init():
    try:
        g_obj_loop.set_debug(procVariable.debug)
        print("aioevent is {} modle".format(g_obj_loop.get_debug()))
        logging.getLogger('asyncio').setLevel(calc_config.async_log_level)
        logging.getLogger('aioredis').setLevel(calc_config.redis_log_level)
        logging.getLogger('aiohttp.server').setLevel(calc_config.async_http_log_level)


        __initLog()
        yield from __initLogicDataMgr()
        asyncio.ensure_future(__secTickCallLater())

        sys.stdout.write("-----> All modules start up successfully! <-----")
        sys.stdout.flush()

    except Exception as e:
        exit(0)


if __name__ == "__main__":

    if sys.version_info[0] < 3:
        print("Found Python interpreter less 3.0 version not support: %s \n"%sys.version)
        sys.exit()
    else:
        parser = OptionParser(usage="%prog --rf <runFlag> ", version="%prog 0.3")
        parser.add_option("--rf", "--runFlag", dest="runFlag", help="runFlag debug or release")
        parser.add_option("--gdb", "--gdb", dest="gdb", help="gdb")


        (options, args) = parser.parse_args()

        runFlag = str(options.runFlag)
        gdb = str(options.gdb)

        if gdb == "gdb":
            procVariable.gdb = True

        if runFlag == "debug":
            procVariable.debug = True
        else:
            procVariable.debug = False
            if not procVariable.gdb:
                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
                g_obj_loop = asyncio.get_event_loop()
                pass


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
