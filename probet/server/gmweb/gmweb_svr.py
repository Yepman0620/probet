import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from lib.signalprocesslog import singlePLogger as log
import logging
from aiohttp import web,http
from aiohttp.web_response import ContentCoding
from error.errorCode import exceptionLogic
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib import onlineMgr, pushMgr, handleMgr
from lib.pubSub import pubMgr
from optparse import  OptionParser
from gmweb.proc import procVariable
from gmweb import gmweb_config
from multidict import CIMultiDict
from urllib.parse import unquote
from lib.observer import classSubject
from thirdweb.logic.observer import classPaySuccess
from event.eventDefine import event_pay_success
import uvloop
import asyncio
import signal
import os
import json

g_obj_loop = asyncio.get_event_loop()

@asyncio.coroutine
def __secTickCallLater():

    g_obj_loop.call_later(5, lambda: asyncio.async(__secTickCallLater()))
    logging.info("ticket the service")
    #logging.getLogger("bill").info("test")


@asyncio.coroutine
def handlerWebApp(request):

    objRespHead = CIMultiDict()
    objRespHead["Access-Control-Allow-Origin"] = "*"
    # objRespHead[" Access-Control-Allow-Methods"]="POST, GET, OPTIONS，PUT, DELETE"
    # objRespHead["Access-Control-Allow-Headers"] = "Authentication,Origin, X-Requested-With, Content-Type, Accept"
    objRespHead["Content-Type"] = "application/json"
    objResp = web.Response()
    objResp.headers.extend(objRespHead)
    #objResp.enable_compression(ContentCoding.gzip)
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
                    dictParams={'srcIp':request.remote}
                    ret = yield from request.read()
                    print(ret)
                    ret=json.loads(ret.decode())
                    dictParams.update(ret)
                    if len(ret) > 0:
                        bytesResponse = yield from objHandleFunction(dictParams)
                    else:
                        bytesResponse = yield from objHandleFunction({})

                    if bytesResponse is None:
                        #objResp.body = b'{"ret":0,"retDes":"","data":""}'
                        objResp.body = b'{"ret":0,"retDes":"","data":""}'
                        # return web.Response(headers=objRespHead,text='{"ret":0,"retDes":"","data":""}')
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
                            # return web.Response(text='{"ret":1,"retDes":"param invalid","data":""}')
                            return objResp

                        dicHandleParam[listEachVar[0]] = unquote(listEachVar[1])

                objHandleFunction = handleMgr.HandleImporter.getInstance().get_handler(strHandlerName)
                if objHandleFunction is None:
                    objResp._status = 404
                    objResp.body = b'{"ret":1,"retDes":"param invalid","data":""}'
                    # return web.Response(text='{"ret":1,"retDes":"param invalid","data":""}')
                    return objResp
                else:
                    dicHandleParam['srcIp']=request.remote
                    bytesResponse = yield from objHandleFunction(dicHandleParam)
                    if bytesResponse is None:
                        objResp.body = b'{"ret":0,"retDes":"","data":""}'

                    else:
                        objResp.body = bytesResponse

                    return objResp

        except exceptionLogic as e:
            logging.error(repr(e))
            objResp.body = json.dumps({"ret": e.iErrorNum, "retDes": e.strMsgDes, "data": ""})
            return objResp
        except Exception as e:
            logging.exception(e)
            if procVariable.debug:
                objResp.body = json.dumps({"ret": 2, "retDes": repr(e), "data": ""})
                # return web.Response(text=body)
            else:

                objResp.body = json.dumps({"ret": 2, "retDes":"inner server error", "data": ""})
                # return web.Response(text=body)

            return objResp

    else:
        objResp._status = 400
        objResp.body = '{"ret":1,"retDes":"path invalid path","data":""}'
        # return web.Response(text=body)
        return objResp

def __stopServer():
    pass

def __initLog():
    log.initLogger(os.path.dirname(os.path.realpath(__file__)) + "/../logdata/", "gmweb",logging.NOTSET)
    #添加日志管理器
    log.initLogger(os.path.dirname(os.path.realpath(__file__)) + "/../logdata/", "bill", logging.DEBUG)

def __initHandle():
    handleMgr.HandleImporter('handle',os.path.dirname(os.path.realpath(__file__)) ,'*.py',"gmweb.")
    handleMgr.HandleImporter.getInstance().load_all()

@asyncio.coroutine
def __initLogicDataMgr():
    classSqlBaseMgr()
    classSqlBaseMgr(__instanceName__='probet_oss')
    if procVariable.debug:
        yield from classSqlBaseMgr.getInstance(instanceName='probet_oss').connetSql(gmweb_config.mysqlAddress_debug, 3306,
                                                                                  'root',gmweb_config.mysqlPwd_debug,'probet_oss',
                                                                                  g_obj_loop,'utf8')

        yield from classSqlBaseMgr.getInstance().connetSql(gmweb_config.mysqlAddress_debug, 3306,
                                                           'root', gmweb_config.mysqlPwd_debug, 'probet_data',
                                                           g_obj_loop)
        classDataBaseMgr(
            gmweb_config.redis_config_debug, g_obj_loop,procVariable.debug,  1, 1)
    else:

        yield from classSqlBaseMgr.getInstance(instanceName='probet_oss').connetSql(gmweb_config.mysqlAddress, 3306,
                                                                                  'root', gmweb_config.mysqlPwd,
                                                                                  'probet_oss',
                                                                                  g_obj_loop, 'utf8')

        yield from classSqlBaseMgr.getInstance().connetSql(gmweb_config.mysqlAddress, 3306,
                                                           'root', gmweb_config.mysqlPwd, 'probet_data',
                                                           g_obj_loop)
        classDataBaseMgr(gmweb_config.redis_config, g_obj_loop,procVariable.debug, 1,1)

    yield from classDataBaseMgr.getInstance().connectRedis()
    yield from classDataBaseMgr.getInstance().loadRedisLuaScript()

@asyncio.coroutine
def __initWebServer():
    server = web.Server(handlerWebApp)
    yield from g_obj_loop.create_server(server, "0.0.0.0", 8082)


@asyncio.coroutine
def __initPushData():
    if procVariable.debug:
        pushMgr.classPushMgr(gmweb_config.redis_push_config_debug, g_obj_loop)
    else:
        pushMgr.classPushMgr(gmweb_config.redis_push_config, g_obj_loop)

    yield from pushMgr.classPushMgr.getInstance().connectRedis()



@asyncio.coroutine
def __initOnline():

    if procVariable.debug:
        onlineMgr.classOnlineMgr(gmweb_config.redis_online_config_debug,
                                                                   g_obj_loop, 2, 2)
    else:
        onlineMgr.classOnlineMgr(gmweb_config.redis_online_config,
                                                                   g_obj_loop)

    yield from onlineMgr.classOnlineMgr.getInstance().connectRedis()

@asyncio.coroutine
def __initBroadCastData():

    if procVariable.debug:
        pubMgr.classPubMgr(
            gmweb_config.all2connect_broadcast_queue_key,
            gmweb_config.redis_debug_address_for_push,
            gmweb_config.redis_pwd,
            gmweb_config.redis_push_db,
            g_obj_loop, 2, 2,__instanceName__="broadCastPub")

    else:
        pubMgr.classPubMgr(
            gmweb_config.all2connect_broadcast_queue_key,
            gmweb_config.redis_address_for_push,
            gmweb_config.redis_pwd,
            gmweb_config.redis_push_db,
            g_obj_loop, 5, 5,__instanceName__="broadCastPub")

    yield from pubMgr.classPubMgr.getInstance("broadCastPub").connectRedis()


@asyncio.coroutine
def __initPubSubMgr():

    if procVariable.debug:

        pubMgr.classPubMgr(
            gmweb_config.gm2result_queue_key,
            gmweb_config.redis_debug_address_for_cross,
            gmweb_config.redis_pwd, gmweb_config.redis_fifo_cross_db,
            g_obj_loop, 2, 2,__instanceName__="resultPub")

    else:
        pubMgr.classPubMgr(
            gmweb_config.gm2result_queue_key,
            gmweb_config.redis_address_for_cross,
            gmweb_config.redis_pwd, gmweb_config.redis_fifo_cross_db,
            g_obj_loop,__instanceName__="resultPub")

    yield from pubMgr.classPubMgr.getInstance("resultPub").connectRedis()

def __initEvent():
    classSubject()
    classSubject.getInstance().attach(classPaySuccess.classPaySuccessForRebateActive(event_pay_success))


@asyncio.coroutine
def init():
    try:
        g_obj_loop.set_debug(procVariable.debug)
        # app=web.Application(debug=procVariable.debug)
        # app.add_routes(routes)
        print("aioevent is {} modle".format(g_obj_loop.get_debug()))
        logging.getLogger('asyncio').setLevel(gmweb_config.async_log_level)
        logging.getLogger('aioredis').setLevel(gmweb_config.redis_log_level)
        logging.getLogger('aiohttp.server').setLevel(gmweb_config.async_http_log_level)


        __initLog()
        __initEvent()
        __initHandle()
        yield from __initLogicDataMgr()
        yield from __initWebServer()
        yield from __initOnline()
        yield from __initPushData()
        yield from __initPubSubMgr()
        yield from __initBroadCastData()

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