import re
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")
from lib.signalprocesslog import singlePLogger as log
import logging
from aiohttp import web,http
from aiohttp.web_response import ContentCoding
from error.errorCode import exceptionLogic
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from lib import onlineMgr, pushMgr, handleMgr
from optparse import  OptionParser
from appweb.proc import procVariable
from appweb import appweb_config
from multidict import CIMultiDict
from urllib.parse import unquote
import uvloop
import traceback
import asyncio
import signal
import os
import json

g_obj_loop = asyncio.get_event_loop()



@asyncio.coroutine
def handlerWebApp(request):

    objRespHead = CIMultiDict()

    objRespHead["Access-Control-Allow-Origin"] = "*"
    #objRespHead["Access-Control-Allow-Headers"] = "Authentication,Origin, X-Requested-With, Content-Type, Accept"
    objRespHead["Content-Type"] = "application/json"
    objResp = web.Response()
    objResp.headers.extend(objRespHead)
    objResp.enable_compression(ContentCoding.gzip)
    http.SERVER_SOFTWARE = "soft probet"

    if len(request.path) >= 0 and len(request.path) <= 128:

        try:

            if request.method == "POST":
                strHandlerName = request.path[1:]
                objHandleFunction = handleMgr.HandleImporter.getInstance().get_handler(strHandlerName)
                if objHandleFunction is None:
                    objResp._status = 404
                    objResp.body = b'{"ret":0,"retDes":"","data":""}'
                    return objResp
                else:
                    dictParam = {"srcIp":request.remote,"resp":objResp,"request":request}
                    if request.headers["Content-Type"].find("multipart/form-data") >= 0:
                        ret = yield from request.post()
                        dictParam.update(ret)
                        bytesResponse = yield from objHandleFunction(dictParam)
                    else:
                        #default application/json
                        ret = yield from request.read()
                        dictParam.update(json.loads(ret.decode()))
                        bytesResponse = yield from objHandleFunction(dictParam)

                    if bytesResponse is None:
                        objResp.body = b'{"ret":0,"retDes":"","data":""}'
                        return objResp
                    else:
                        objResp.body = bytesResponse.decode()

                    return objResp
            elif request.method == "GET":
                dicHandleParam = {"srcIp":request.remote,"resp":objResp,"request":request}
                strHandlerName = request.path[1:]
                if len(request.query_string) <= 0:
                    pass
                else:
                    listParam = request.query_string.split('&')
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
                        objResp.body = bytesResponse.decode()
                    return objResp
            elif request.method == "OPTIONS":
                objRespHead["Access-Control-Allow-Methods"] = "GET, POST"
                objResp.body = b''
                return objResp
            else:
                objResp._status = 403
                objResp.body = b'{"ret":1,"retDes":"not allowed","data":""}'
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
    log.initLogger(os.path.dirname(os.path.realpath(__file__)) + "/../logdata/", "appweb",logging.DEBUG)
    log.initLogger(os.path.dirname(os.path.realpath(__file__)) + "/../logdata/", "bill", logging.DEBUG)


def __initHandle():
    handleMgr.HandleImporter('handle',os.path.dirname(os.path.realpath(__file__)) ,'*.py',"appweb.")
    handleMgr.HandleImporter.getInstance().load_all()

@asyncio.coroutine
def __initLogicDataMgr():
    if procVariable.debug:
        classDataBaseMgr(
            appweb_config.redis_config_debug, g_obj_loop,procVariable.debug, 1, 1)
    else:
        classDataBaseMgr(appweb_config.redis_config, g_obj_loop,procVariable.debug,1,1)

    yield from classDataBaseMgr.getInstance().connectRedis()
    yield from classDataBaseMgr.getInstance().loadRedisLuaScript()


    classSqlBaseMgr()

    if procVariable.debug:
        yield from classSqlBaseMgr.getInstance().connetSql(appweb_config.mysqlAddress_debug, 3306,
                                                           'root', appweb_config.mysqlPwd_debug, 'probet_data',
                                                           g_obj_loop)

    else:
        yield from classSqlBaseMgr.getInstance().connetSql(appweb_config.mysqlAddress, 3306,
                                                           'root', appweb_config.mysqlPwd, 'probet_data',
                                                           g_obj_loop)



@asyncio.coroutine
def __initAppWebServer():
    server = web.Server(handlerWebApp)
    yield from g_obj_loop.create_server(server, "0.0.0.0", 8081)


@asyncio.coroutine
def __initPushData():
    if procVariable.debug:
        pushMgr.classPushMgr(appweb_config.redis_push_config_debug, g_obj_loop)
    else:
        pushMgr.classPushMgr(appweb_config.redis_push_config, g_obj_loop)


    yield from pushMgr.classPushMgr.getInstance().connectRedis()



@asyncio.coroutine
def __initOnline():

    if procVariable.debug:
        onlineMgr.classOnlineMgr(appweb_config.redis_online_config_debug,
                                                                   g_obj_loop, 2, 2)
    else:
        onlineMgr.classOnlineMgr(appweb_config.redis_online_config,
                                                                   g_obj_loop)

    yield from onlineMgr.classOnlineMgr.getInstance().connectRedis()


@asyncio.coroutine
def init():
    try:
        g_obj_loop.set_debug(procVariable.debug)
        print("aioevent is {} modle".format(g_obj_loop.get_debug()))
        logging.getLogger('asyncio').setLevel(appweb_config.async_log_level)
        logging.getLogger('aioredis').setLevel(appweb_config.redis_log_level)
        logging.getLogger('aiohttp.server').setLevel(appweb_config.async_http_log_level)


        __initLog()

        __initHandle()
        yield from __initLogicDataMgr()
        yield from __initAppWebServer()
        yield from __initOnline()
        yield from __initPushData()

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