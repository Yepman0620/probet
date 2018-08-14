import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from lib.signalprocesslog import singlePLogger as log
from osssvr.proc import procVariable
from optparse import OptionParser
from osssvr.singleton import singletonDefine
import logging
from osssvr import oss_config
from aiomysql.sa import create_engine
from osssvr.utils.models import FilePos
from lib.timehelp import timeHelp
import traceback
import asyncio
import signal
import os
import uvloop


g_obj_loop = asyncio.get_event_loop()


@asyncio.coroutine
def __secTickCallLater():

    try:

        yield from singletonDefine.g_obj_LogicOssFileMgr.statistics_log()
        g_obj_loop.call_later(1, lambda: asyncio.async(__secTickCallLater()))

    except Exception as e:
        logging.error('{}, {}'.format(timeHelp.getNow(), traceback.format_exc()))

    logging.info("ticket the service")

@asyncio.coroutine
def __initData():

    classSqlBaseMgr()

    if procVariable.debug:
        yield from classSqlBaseMgr.getInstance().connetSql(oss_config.mysqlAddress_debug, 3306,
                                                           'root', oss_config.mysqlPwd_debug, 'probet_oss',
                                                           g_obj_loop)

        singletonDefine.g_obj_dbMysqlMgr = yield from create_engine(host=oss_config.mysqlAddress_debug, port=3306,
                                       user='root', password=oss_config.mysqlPwd_debug, db='probet_oss',
                                       loop=g_obj_loop)
    else:
        yield from classSqlBaseMgr.getInstance().connetSql(oss_config.mysqlAddress, 3306,
                                                           'root', oss_config.mysqlPwd, 'probet_oss',
                                                           g_obj_loop)

        singletonDefine.g_obj_dbMysqlMgr = yield from create_engine(host=oss_config.mysqlAddress, port=3306,
                                                                    user='root', password=oss_config.mysqlPwd, db='probet_oss',
                                                                    loop=g_obj_loop)


    #TODO check the filepos
    selectSql = FilePos.getSelectSqlObj(procVariable.host)
    engine = classSqlBaseMgr.getInstance().getEngine()
    with (yield from engine) as conn:
        result = yield from conn.execute(selectSql)
        if result.rowcount <= 0:

            #初始化
            logging.info("init the file pos mysql table")
            objInsertSql = FilePos.getInsertSqlObj(procVariable.host,oss_config.billFilaPath,0,0)

            trans = yield from conn.begin()
            try:
                yield from conn.execute(objInsertSql)
            except Exception as e:
                # TODO log error
                logging.exception(e)
                yield from trans.rollback()
            else:
                yield from trans.commit()

                singletonDefine.g_obj_LogicOssFileMgr.init_file(oss_config.billFilaPath, 0)

        else:
            for var_row in result:
                logging.info("oss row is -->{}".format(var_row))
                if not timeHelp.isSameDay(var_row.lastLogTime.timestamp(),timeHelp.getNow()):
                    logging.error("bill log is between two days")
                    #TODO 把这个间隔时间段内的读取完毕
                    singletonDefine.g_obj_LogicOssFileMgr.init_file(str(var_row.fileName), 0)
                else:
                    singletonDefine.g_obj_LogicOssFileMgr.init_file(str(var_row.fileName), var_row.seekPos, var_row.lastLogTime.timestamp())#int(var_row.seekPos))

def __stopServer():
    pass

def __initLog():
    log.initLogger(os.path.dirname(os.path.realpath(__file__)) + "/../logdata/", "oss_svr",logging.NOTSET)

@asyncio.coroutine
def init():
    try:
        g_obj_loop.set_debug(procVariable.debug)
        logging.getLogger('asyncio').setLevel(logging.WARNING)
        logging.getLogger('aioredis').setLevel(logging.WARNING)

        __initLog()

        yield from __initData()

        g_obj_loop.call_later(3,lambda: asyncio.async(__secTickCallLater()))

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
        parser.add_option("--host","--host", dest="host",help="host to save to filepos")

        (options, args) = parser.parse_args()

        runFlag = str(options.runFlag)
        gdb = str(options.gdb)
        host= str(options.host)


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

        if len(host) <= 0 or (options.host is None):
            #ubuntu 下使用
            #procVariable.host = os.system("cat /etc/hostname")
            #linux 下
            import socket
            procVariable.host = socket.getfqdn(socket.gethostname())
            if len(procVariable.host) <= 0:
                print("host name can not find")
                exit()



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
        logging.error(traceback.format_exc())
        exit(0)
    finally:
        g_obj_loop.close()