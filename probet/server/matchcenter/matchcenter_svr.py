import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")
from lib.signalprocesslog import singlePLogger as log
import logging
import asyncio
import traceback
import signal
import os
import sys
import json
from error.errorCode import exceptionLogic
from matchcenter.matchlogic import matchInitLogic
from matchcenter.proc import procVariable
from optparse import OptionParser
from matchcenter import matchcenter_config
from datawrapper.dataBaseMgr import classDataBaseMgr
import uvloop
import socket


g_obj_loop = asyncio.get_event_loop()


@asyncio.coroutine
def __secTickCallLater():
    while True:
        try:
            yield from matchInitLogic.updateMatchPlatform()
        except Exception as e:
            logging.exception(e)
            logging.error(traceback.format_exc())
        finally:
            #pass
            yield from asyncio.sleep(5)


def __initLog():
    log.initLogger(os.path.dirname(os.path.realpath(__file__)) + "/../logdata/","matchcenter_svr", matchcenter_config.log_level)


@asyncio.coroutine
def initDataCenterRedis():
    if procVariable.debug:
        classDataBaseMgr(matchcenter_config.redis_config_debug, g_obj_loop,procVariable.debug,  1, 1)

    else:
        classDataBaseMgr(matchcenter_config.redis_config,g_obj_loop,procVariable.debug,  2, 2)

    yield from classDataBaseMgr.getInstance().connectRedis()
    yield from classDataBaseMgr.getInstance().loadRedisLuaScript()



def __stopServer():
    pass



@asyncio.coroutine
def init():
    try:
        g_obj_loop.set_debug(procVariable.debug)
        print("aioevent is {} modle".format(g_obj_loop.get_debug()))
        logging.getLogger('asyncio').setLevel(matchcenter_config.async_log_level)
        logging.getLogger('aioredis').setLevel(matchcenter_config.redis_log_level)

        __initLog()


        yield from initDataCenterRedis()
        asyncio.ensure_future(__secTickCallLater())


        sys.stdout.write("-----> All modules start up successfully! <-----")
        sys.stdout.flush()

    except:
        exit(0)


if "__main__" == __name__:

    if sys.version_info[0] < 3:
        print("Found Python interpreter less 3.0 version not support: %s \n"%sys.version)
        sys.exit()
    else:
        parser = OptionParser(usage="%prog --rf <runFlag> --gdb <gdb> --ds <ds>", version="%prog 0.3")
        parser.add_option("--rf", "--runFlag", dest="runFlag", help="runFlag debug or release")
        parser.add_option("--gdb", "--gdb", dest="gdb", help="gdb")
        parser.add_option("--ds", "--datasrc", dest="datasrc", help="data src")

        (options, args) = parser.parse_args()

        runFlag = str(options.runFlag)
        gdb = str(options.gdb)
        ds = str(options.datasrc)

        if gdb == "gdb":
            procVariable.gdb = True

        if runFlag == 'debug':
            procVariable.debug = True
        elif runFlag == 'release':
            procVariable.debug = False
            if not procVariable.gdb:
                #asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
                g_obj_loop = asyncio.get_event_loop()
        else:
            print("runFlag is not valid please --help the detail")
            exit(0)

        if ds == "debug":
            procVariable.dataDebug = True

    #register the signal stop the loop
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
        logging.error(traceback.format_exc())

    finally:
        g_obj_loop.close()