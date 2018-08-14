import sys
import os

import aiohttp

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")
from gmweb.handle.pinbo.check_pingbo_wagers import todo_pingbo_wagers, updateBetOrder
from thirdweb.tools.pingbo_wagers import get_settle_wagers
from lib.signalprocesslog import singlePLogger as log
import logging
from aiohttp import web,http
from aiohttp.web_response import ContentCoding
from error.errorCode import exceptionLogic
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from lib import onlineMgr, pushMgr, handleMgr
from lib.observer import classSubject
from event.eventDefine import event_pay_success,event_exchange_coin
from thirdweb.logic.observer import classPaySuccess
from optparse import  OptionParser
from thirdweb.proc import procVariable
from thirdweb import thirdweb_config
from multidict import CIMultiDict
from urllib.parse import unquote
import uvloop
import traceback
import asyncio
import signal
import os
import json

g_obj_loop = asyncio.get_event_loop()
g_seesion=None


@asyncio.coroutine
def __secTickCallLater():


    g_obj_loop.call_later(5, lambda: asyncio.async(__secTickCallLater()))
    logging.info("ticket the service")


@asyncio.coroutine
def handlerWebApp(request):

    objRespHead = CIMultiDict()
    #objRespHead["Access-Control-Allow-Origin"] = "*"
    #objRespHead["Access-Control-Allow-Headers"] = "Authentication,Origin, X-Requested-With, Content-Type, Accept"
    objRespHead["Content-Type"] = "text/plain"
    objResp = web.Response()
    objResp.headers.extend(objRespHead)
    objResp.enable_compression(ContentCoding.gzip)
    http.SERVER_SOFTWARE = "soft probet"

    if len(request.path) >= 0 and len(request.path) <= 128:

        try:

            if request.method != "GET":
                strHandlerName = request.path[1:]
                objHandleFunction = handleMgr.HandleImporter.getInstance().get_handler(strHandlerName)

                if objHandleFunction is None:
                    objResp._status = 404
                    objResp.body = b'{"ret":0,"retDes":"","data":""}'
                    return objResp
                else:

                    ret = yield from request.read()
                    logging.info(ret)
                    bytesResponse = yield from objHandleFunction(ret)

                    if bytesResponse is None:
                        objResp.body = b'{"ret":0,"retDes":"","data":""}'

                        return objResp
                    else:
                        objResp.body = bytesResponse

                    return objResp

            else:
                dicHandleParam = {}
                strHandlerName = request.path[1:]
                if len(request.query_string) <= 0:
                    pass
                else:
                    listParam = request.query_string.split('&')
                    dicHandleParam = {}
                    for param in listParam:
                        listEachVar = param.split('=')
                        if len(listEachVar) < 2:

                            objResp.body = b'{"ret":1,"retDes":"param invalid","data":""}'
                            return objResp

                        dicHandleParam[listEachVar[0]] = unquote(listEachVar[1])

                objHandleFunction = handleMgr.HandleImporter.getInstance().get_handler(strHandlerName)
                if objHandleFunction is None:
                    objResp._status = 404
                    objResp.body = b'{"ret":1,"retDes":"param invalid","data":""}'
                    return objResp
                else:
                    bytesResponse = yield from objHandleFunction(dicHandleParam)
                    if bytesResponse is None:
                        objResp.body = b'{"ret":0,"retDes":"","data":""}'
                        return objResp
                    else:
                        objResp.body = bytesResponse
                    return objResp

        except exceptionLogic as e:
            logging.exception(e)
            objResp.body = json.dumps({"ret": e.iErrorNum, "retDes": e.strMsgDes, "data": ""})
            return objResp
        except Exception as e:

            logging.exception(e)
            if procVariable.debug:
                objResp.body = json.dumps({"ret": 2, "retDes": repr(e), "data": ""})
            else:
                objResp.body = json.dumps({"ret": 2, "retDes":"inner server error", "data": ""})
            return objResp

    else:
        objResp._status = 400
        objResp.body = b'{"ret":1,"retDes":"path invalid path","data":""}'
        return objResp


def __stopServer():
    pass

def __initLog():
    log.initLogger(os.path.dirname(os.path.realpath(__file__)) + "/../logdata/", "thirdweb",logging.NOTSET)
    log.initLogger(os.path.dirname(os.path.realpath(__file__)) + "/../logdata/", "bill", logging.DEBUG)


def __initHandle():
    handleMgr.HandleImporter('handle',os.path.dirname(os.path.realpath(__file__)) ,'*.py',"thirdweb.")
    handleMgr.HandleImporter.getInstance().load_all()

def __initEvent():
    classSubject()

    classSubject.getInstance().attach(classPaySuccess.classPaySuccessForRebateActive(event_pay_success))
    classSubject.getInstance().attach(classPaySuccess.classPaySuccessForRebateActive(event_exchange_coin))


@asyncio.coroutine
def __update(session):
    try:
        retList=yield from get_settle_wagers(session)
        update_count = 0
        if retList is None:
            logging.exception("retList is NoneType!")

        total_count = len(retList)
        engine = classSqlBaseMgr.getInstance().getEngine()
        with (yield from engine) as mysql_conn:
            for x in retList:
                with (yield from classSqlBaseMgr.getInstance().objDbMysqlMgr) as conn:
                    is_exist_sql = "select * from dj_pinbo_wagers WHERE wagerId=%s "
                    is_exist = yield from conn.execute(is_exist_sql,[x['wagerId']])
                    is_exist = yield from is_exist.fetchone()
                    if is_exist.status != 'SETTLED' and x['status'] == 'SETTLED':
                        strAccount = x["loginId"][7:]
                        objPlayerData, objPlayerLock = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccount)
                        if objPlayerData is None:
                            logging.error("accountId[{}] not valid".format(strAccount))
                        else:
                            # 不可提现额度减投注额，直到0为止
                            if objPlayerData.iNotDrawingCoin - x['toRisk'] * 100 < 0:
                                objPlayerData.iNotDrawingCoin = 0
                            else:
                                objPlayerData.iNotDrawingCoin -= int(x['toRisk'] * 100)
                            yield from classDataBaseMgr.getInstance().setPlayerDataByLock(objPlayerData, objPlayerLock)
                ret = yield from updateBetOrder(x,mysql_conn)
                if ret[0] is True:
                    if ret[1] == 'update':
                        update_count += 1

        logging.debug('total pingbo_wagers[{}],update success[{}]'.format(total_count,update_count))
    except Exception as e:
        logging.exception(e)

    g_obj_loop.call_later(3*60, lambda: asyncio.async(__update(session)))


@asyncio.coroutine
def __initLogicDataMgr():
    if procVariable.debug:
        classDataBaseMgr(
            thirdweb_config.redis_config_debug, g_obj_loop,procVariable.debug,  1, 1)
    else:
        classDataBaseMgr(thirdweb_config.redis_config, g_obj_loop, procVariable.debug, 1, 1)

    yield from classDataBaseMgr.getInstance().connectRedis()
    yield from classDataBaseMgr.getInstance().loadRedisLuaScript()

    classSqlBaseMgr()

    if procVariable.debug:
        yield from classSqlBaseMgr.getInstance().connetSql(thirdweb_config.mysqlAddress_debug, 3306,
                                                           'root', thirdweb_config.mysqlPwd_debug, 'probet_data',
                                                           g_obj_loop)
    else:
        yield from classSqlBaseMgr.getInstance().connetSql(thirdweb_config.mysqlAddress, 3306,
                                                           'root', thirdweb_config.mysqlPwd, 'probet_data',
                                                           g_obj_loop)


@asyncio.coroutine
def __initWebServer():
    server = web.Server(handlerWebApp)
    yield from g_obj_loop.create_server(server, "0.0.0.0", 8083)


@asyncio.coroutine
def __initPushData():
    if procVariable.debug:
        pushMgr.classPushMgr(thirdweb_config.redis_push_config_debug, g_obj_loop)
    else:
        pushMgr.classPushMgr(thirdweb_config.redis_push_config, g_obj_loop)


    yield from pushMgr.classPushMgr.getInstance().connectRedis()



@asyncio.coroutine
def __initOnline():

    if procVariable.debug:
        onlineMgr.classOnlineMgr(thirdweb_config.redis_online_config_debug,
                                 g_obj_loop, 2, 2)
    else:
        onlineMgr.classOnlineMgr(thirdweb_config.redis_online_config,
                                 g_obj_loop)

    yield from onlineMgr.classOnlineMgr.getInstance().connectRedis()


@asyncio.coroutine
def init():
    try:
        g_obj_loop.set_debug(procVariable.debug)
        print("aioevent is {} modle".format(g_obj_loop.get_debug()))
        logging.getLogger('asyncio').setLevel(thirdweb_config.async_log_level)
        logging.getLogger('aioredis').setLevel(thirdweb_config.redis_log_level)
        logging.getLogger('aiohttp.server').setLevel(thirdweb_config.async_http_log_level)


        __initLog()

        __initHandle()
        __initEvent()
        yield from __initLogicDataMgr()
        yield from __initWebServer()
        yield from __initOnline()
        yield from __initPushData()
        asyncio.ensure_future(__secTickCallLater())
        global g_session
        g_session=aiohttp.ClientSession(conn_timeout=180, read_timeout=180)
        g_obj_loop.call_later(5, lambda: asyncio.async(__update(g_session)))
        sys.stdout.write("-----> All modules start up successfully! <-----")
        sys.stdout.flush()

    except Exception as e:
        logging.exception(e)
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
        g_seesion.close()