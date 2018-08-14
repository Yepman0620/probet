import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")
#from lib.multiprocesslogbysyshandler import multiPLogger as log
from lib.multiprocesslogbylogserver import multiPLogger as log
import logging
import logging.handlers
import asyncio
import traceback
import signal
import sys
import pickle
import time
from logic.proc import procVariable
from optparse import OptionParser
from lib import pushMgr, onlineMgr, fifoMgr
from lib.pubSub import pubMgr
from logic import logic_config
from config import zoneConfig
from logic.register import handleRegister
from datawrapper import dataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from error.errorCode import exceptionLogic,errorLogic
import uvloop


g_obj_loop = asyncio.get_event_loop()

@asyncio.coroutine
def handlerConnectMessage(head_message,body_message):
    try:

        beginTime = time.time()
        #logging.7('logic').debug("handlerConnectMessage {} {}".format(head_message,body_message))
        objHead = pickle.loads(head_message)
        fbBody = pickle.loads(body_message)

        logging.getLogger('logic').debug("accountId[{}] clientUdid[{}] clientIp[{}] msgId[{}] fbBody[{}]".format(objHead.strAccountId,objHead.strClientUdid,objHead.strClientIp,objHead.strMsgId,fbBody))

        funHandle = handleRegister.g_obj_handlerRegister.get(objHead.strMsgId,None)
        if funHandle == None:
            logging.getLogger('logic').debug("msgid{} is not regist".format(objHead.strMsgId))
            return

        objBody = None
        try:
            objBody = yield from funHandle(objHead,fbBody)

        except exceptionLogic as e:
            ret = e.iErrorNum
            retDes = e.strMsgDes
            logging.getLogger('logic').error("accountId[{}] udid[{}] error[{}] des[{}]".format(objHead.strAccountId,objHead.strClientUdid,ret,retDes))
            yield from fifoMgr.classFIFOMgr.getInstance().publish(objHead, {'ret':ret,"retDes":retDes})
        except:
            logging.getLogger('logic').error(traceback.format_exc())
            ret = errorLogic.sys_unknow_error[0]
            retDes = errorLogic.sys_unknow_error[1]
            yield from fifoMgr.classFIFOMgr.getInstance().publish(objHead, {'ret':ret,"retDes":retDes})


        yield from fifoMgr.classFIFOMgr.getInstance().publish(objHead, objBody)

        endTime = time.time()

        logging.getLogger('logic').info("handle msg[{}] use time [{}]".format(objHead.strMsgId,endTime - beginTime))

    except:
        logging.getLogger('logic').error(traceback.format_exc())


def __initLog():
    #log.initLogger(os.path.dirname(os.path.realpath(__file__)) + "/../logdata/","logic_svr")
    #log.initLogger(logic_config.log_level,logging.handlers.SysLogHandler.LOG_LOCAL0,procVariable.debug)
    log.initLogger(logic_config.log_level,os.path.dirname(os.path.realpath(__file__)) +  "/../logdata/","logic","logic_svr_{}.log".format(procVariable.work_id))
    log.initLogger(logic_config.log_level,os.path.dirname(os.path.realpath(__file__)) + "/../logdata/", "bill")
    #log.initLogger(logic_config.log_level, "/../logdata/bill_{}.log".format(procVariable.work_id))


@asyncio.coroutine
def __initFiFo():

    if procVariable.debug:
        fifoMgr.classFIFOMgr(logic_config.logic2connect_queue_key.format(procVariable.group_id),
                                                                  logic_config.connect2logic_queue_key.format(procVariable.group_id),

                                                                  logic_config.redis_address_for_local, zoneConfig.redis_pwd, zoneConfig.redis_fifo_db,
                                                                  g_obj_loop, 2, 2)
    else:
        fifoMgr.classFIFOMgr(logic_config.logic2connect_queue_key.format(procVariable.group_id),
                                                                  logic_config.connect2logic_queue_key.format(procVariable.group_id),

                                                                  logic_config.redis_address_for_local,
                                                                  zoneConfig.redis_pwd, zoneConfig.redis_fifo_db,
                                                                  g_obj_loop)

    yield from fifoMgr.classFIFOMgr.getInstance().connectRedis()

    fifoMgr.classFIFOMgr.getInstance().registerCall(handlerConnectMessage)
    fifoMgr.classFIFOMgr.getInstance().bDebug = procVariable.debug


    if procVariable.rmQueue == 1:
        yield from fifoMgr.classFIFOMgr.getInstance().cleanFifoQueue()


@asyncio.coroutine
def __initData():
    if procVariable.debug:
        dataBaseMgr.classDataBaseMgr(logic_config.redis_config_debug,g_obj_loop,procVariable.debug, 2, 2)

    else:
        dataBaseMgr.classDataBaseMgr(logic_config.redis_config,g_obj_loop,procVariable.debug)

    yield from dataBaseMgr.classDataBaseMgr.getInstance().connectRedis()
    yield from dataBaseMgr.classDataBaseMgr.getInstance().loadRedisLuaScript()

    classSqlBaseMgr()

    if procVariable.debug:
        yield from classSqlBaseMgr.getInstance().connetSql(logic_config.mysqlAddress_debug, 3306,
                                                           'root', logic_config.mysqlPwd_debug, 'probet_data',
                                                           g_obj_loop)
    else:
        yield from classSqlBaseMgr.getInstance().connetSql(logic_config.mysqlAddress, 3306,
                                                           'root', logic_config.mysqlPwd, 'probet_data',
                                                           g_obj_loop)


@asyncio.coroutine
def __initBroadCastData():

    if procVariable.debug:
        pubMgr.classPubMgr(
            logic_config.all2connect_broadcast_queue_key,
            logic_config.redis_debug_address_for_push,
            logic_config.redis_pwd,
            logic_config.redis_push_db,
            g_obj_loop, 2, 2)

    else:
        pubMgr.classPubMgr(
            logic_config.all2connect_broadcast_queue_key,
            logic_config.redis_address_for_push,
            logic_config.redis_pwd,
            logic_config.redis_push_db,
            g_obj_loop, 5, 5)

    yield from pubMgr.classPubMgr.getInstance().connectRedis()

@asyncio.coroutine
def __initPushData():
    if procVariable.debug:
        pushMgr.classPushMgr(logic_config.redis_push_config_debug,g_obj_loop)
    else:
        pushMgr.classPushMgr(logic_config.redis_push_config,g_obj_loop)

    yield from pushMgr.classPushMgr.getInstance().connectRedis()


@asyncio.coroutine
def __initOnline():

    if procVariable.debug:
        onlineMgr.classOnlineMgr(logic_config.redis_online_config_debug,
                                                                    g_obj_loop,2,2)
    else:
        onlineMgr.classOnlineMgr(logic_config.redis_online_config,
                                                                    g_obj_loop)

    yield from onlineMgr.classOnlineMgr.getInstance().connectRedis()


@asyncio.coroutine
def __initUpdate():
    #print(type(singletonDefine.g_obj_websocket))
    #yield from asyncio.gather(singletonDefine.g_obj_fifoMgr.updateFifoChannel(),__secTickCallLater(),__setMinuteCallLater())
    asyncio.ensure_future(fifoMgr.classFIFOMgr.getInstance().updateFifoChannel())
    asyncio.ensure_future(__secTickCallLater())
    asyncio.ensure_future(__setMinuteCallLater())

def __stopServer():
    pass

@asyncio.coroutine
def __secTickCallLater():


    g_obj_loop.call_later(1, lambda: asyncio.async(__secTickCallLater()))


    pass
@asyncio.coroutine
def __setMinuteCallLater():

    #print(asyncio.Task.all_tasks())
    print("*********Total[{}]**********".format(len(asyncio.Task.all_tasks())))
    #if procVariable.debug:
    #    for var_task in asyncio.Task.all_tasks():
    #        print(var_task)

    g_obj_loop.call_later(60, lambda: asyncio.async(__setMinuteCallLater()))
    pass

@asyncio.coroutine
def init():
    try:
        g_obj_loop.set_debug(procVariable.debug)
        print("aioevent is {} modle".format(g_obj_loop.get_debug()))
        logging.getLogger('asyncio').setLevel(logic_config.async_log_level)
        logging.getLogger('aioredis').setLevel(logic_config.redis_log_level)

        __initLog()
        print("init fifo")
        yield from __initFiFo()
        print("init data")
        yield from __initData()
        print("init online")
        yield from __initOnline()
        print("init broadcast")
        yield from __initBroadCastData()
        print("init push")
        yield from __initPushData()
        print("init update")
        #must be the lasted
        yield from __initUpdate()

        sys.stdout.write("-----> All modules start up successfully! <-----")
        sys.stdout.flush()

    except:
        exit(0)


if "__main__" == __name__:

    if sys.version_info[0] < 3:
        print("Found Python interpreter less 3.0 version not support: %s \n"%sys.version)
        sys.exit()
    else:
        #命令行参数
        parser = OptionParser(usage="%prog --rf <runFlag> --wid <workid> --gid <gid> --gcount <gcount> --rmq <rmq> --gdb <gdb> --ds <ds>", version="%prog 0.3")
        parser.add_option("--rf", "--runFlag", dest="runFlag", help="runFlag debug or release")
        parser.add_option("--wid", "--workid", dest="workid", help="workid 1 ~ N")
        parser.add_option("--gid", "--groupid", dest="groupid", help="groupid 1 ~ N")
        parser.add_option("--gcount", "--groupcount", dest="groupcount", help="groupcount 1 ~ N")
        parser.add_option("--rmq", "--rmQueue", dest="rmQueue", help="rm the redis queue between connect and logic")
        parser.add_option("--gdb", "--gdb", dest="gdb", help="gdb")
        parser.add_option("--ds", "--datasrc", dest="datasrc", help="data src")
        parser.add_option("--host", "--host", dest="host", help="host")

        (options, args) = parser.parse_args()

        runFlag = str(options.runFlag)
        workid = str(options.workid)
        groupid = str(options.groupid)
        groupcount = str(options.groupcount)
        rmFlag = str(options.rmQueue)
        gdb = str(options.gdb)
        ds = str(options.datasrc)
        host = str(options.host)

        if gdb == 'gdb':
            procVariable.gdb = True

        if runFlag == 'debug':
            procVariable.debug = True
        elif runFlag == 'release':
            procVariable.debug = False
            if not procVariable.gdb:
                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
                g_obj_loop = asyncio.get_event_loop()

        else:
            print("runFlag is not valid please --help the detail")
            exit(0)
        try:
            procVariable.work_id = int(workid)
            procVariable.group_id = int(groupid)
            procVariable.group_count = int(groupcount)
        except:
            print("work_id not valid please --help the detail")
            exit(0)

        try:
            procVariable.rmQueue = int(rmFlag)
        except:
            print("rmq not valid please --help the detail")
            exit(0)


        if ds == "debug":
            procVariable.dataDebug = True

        if len(host) <= 0 or (options.host is None):
            # ubuntu 下使用
            # procVariable.host = os.system("cat /etc/hostname")
            # linux 下
            import socket

            procVariable.host = socket.getfqdn(socket.gethostname())
            if len(procVariable.host) <= 0:
                print("host name can not find")
                exit()


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

        fifoMgr.classFIFOMgr.getInstance().stop()

        g_obj_loop.stop()
        g_obj_loop.run_forever()
    except:
        logging.getLogger('logic').error(traceback.format_exc())

    finally:
        g_obj_loop.close()