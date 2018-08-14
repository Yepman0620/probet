
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")
from resultcenter.proc import procVariable
from optparse import OptionParser
#from lib.multiprocesslogbysyshandler import multiPLogger as log
from lib.multiprocesslogbylogserver import multiPLogger as log
import logging
import logging.handlers
from resultcenter.register import handleRegister   #要删，注册handler用
import traceback
from resultcenter import result_config
from datawrapper import dataBaseMgr
import asyncio
import signal
import os
import uvloop
from lib import pushMgr,onlineMgr
from lib.pubSub import subMgr



g_obj_loop = asyncio.get_event_loop()


@asyncio.coroutine
def handlerDataCenterMessage(msgHead,msgBody):

    try:

        objHandleFunction = handleRegister.g_obj_handlerRegister.get(msgHead.strMsgId)
        if objHandleFunction is None:
            logging.getLogger('result').error("the msgId{} not find the handle".format(msgHead.strMsgId))
        else:
            yield from objHandleFunction(msgHead,msgBody)
    except Exception as e:
        logging.getLogger('result').error(repr(e))

@asyncio.coroutine
def handlerGmMessage(msgHead,msgBody):

    try:

        objHandleFunction = handleRegister.g_obj_handlerRegister.get(msgHead.strMsgId)
        if objHandleFunction is None:
            logging.getLogger('result').error("the msgId{} not find the handle".format(msgHead.strMsgId))
        else:
            yield from objHandleFunction(msgHead,msgBody)
    except Exception as e:
        logging.getLogger('result').error(repr(e))


def __stopServer():
    pass

@asyncio.coroutine
def __initPubSub():

    if procVariable.debug:
        subMgr.classSubMgr(result_config.gm2result_queue_key,result_config.redis_debug_address_for_cross,
                                                                               result_config.redis_pwd,
                                                                               result_config.redis_fifo_cross_db,
                                                                               g_obj_loop)
    else:

        subMgr.classSubMgr(result_config.gm2result_queue_key,result_config.redis_address_for_cross,
                                                                           result_config.redis_pwd,
                                                                           result_config.redis_fifo_cross_db,
                                                                           g_obj_loop)

    yield from subMgr.classSubMgr.getInstance().connectRedis()

    subMgr.classSubMgr.getInstance().registerCall(handlerDataCenterMessage)


@asyncio.coroutine
def __initUpdate():

    asyncio.ensure_future(subMgr.classSubMgr.getInstance().updatePubSubChannel())

@asyncio.coroutine
def __initData():
    if procVariable.debug:
        dataBaseMgr.classDataBaseMgr(result_config.redis_config_debug,g_obj_loop,procVariable.debug, 2, 2)

    else:
        dataBaseMgr.classDataBaseMgr(result_config.redis_config,g_obj_loop,procVariable.debug)

    yield from dataBaseMgr.classDataBaseMgr.getInstance().connectRedis()
    yield from dataBaseMgr.classDataBaseMgr.getInstance().loadRedisLuaScript()


@asyncio.coroutine
def __initPushData():
    if procVariable.debug:
        pushMgr.classPushMgr(result_config.redis_push_config_debug,g_obj_loop)
    else:
        pushMgr.classPushMgr(result_config.redis_push_config,g_obj_loop)

    yield from pushMgr.classPushMgr.getInstance().connectRedis()


@asyncio.coroutine
def __initOnline():

    if procVariable.debug:
        onlineMgr.classOnlineMgr(result_config.redis_online_config_debug,
                                                                    g_obj_loop,2,2)
    else:
        onlineMgr.classOnlineMgr(result_config.redis_online_config,
                                                                    g_obj_loop)

    yield from onlineMgr.classOnlineMgr.getInstance().connectRedis()



@asyncio.coroutine
def init():
    try:
        g_obj_loop.set_debug(procVariable.debug)
        logging.getLogger('asyncio').setLevel(result_config.async_log_level)
        logging.getLogger('aioredis').setLevel(result_config.redis_log_level)

        __initLog()

        yield from __initPubSub()
        yield from __initData()
        yield from __initPushData()
        yield from __initOnline()


        yield from __initUpdate()

        sys.stdout.write("-----> All modules start up successfully! <-----")
        sys.stdout.flush()

    except Exception as e:
        exit(0)


def __initLog():
    #log.initLogger(result_config.log_level,logging.handlers.SysLogHandler.LOG_LOCAL1)

    log.initLogger(result_config.log_level,os.path.dirname(os.path.realpath(__file__)) + "/../logdata/","result","result_svr_{}.log".format(procVariable.work_id))

if __name__ == "__main__":

    if sys.version_info[0] < 3:
        print("Found Python interpreter less 3.0 version not support: %s \n" % sys.version)
        sys.exit()
    else:
        parser = OptionParser(usage="%prog --rf <runFlag>",
                              version="%prog 0.3")
        parser.add_option("--rf", "--runFlag", dest="runFlag", help="runFlag debug or release")
        parser.add_option("--gdb", "--gdb", dest="gdb", help="gdb")
        parser.add_option("--wid", "--wid", dest="wid", help="wid")
        (options, args) = parser.parse_args()

        runFlag = str(options.runFlag)
        gdb = str(options.gdb)
        wid = str(options.wid)

        if gdb == "gdb":
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

        try:
            procVariable.work_id = int(wid)
        except:
            print("work_id not valid please --help the detail")
            exit(0)

        '''
        try:
            procVariable.rmQueue = int(rmFlag)
        except:
            print("rmq not valid please --help the detail")
            exit(0)
        '''

    # register the signal stop the loop
    stop = asyncio.Future()
    g_obj_loop.add_signal_handler(signal.SIGUSR1, stop.set_result, None)
    signal.signal(signal.SIGUSR1, __stopServer)

    #singal 另外一个参考
    #https://docs.python.org/3/library/asyncio-eventloop.html#executor

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