import sys
import os
#os.environ['PYTHONASYNCIODEBUG'] = '1'
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")
from lib.signalprocesslog import singlePLogger as log
import logging
import asyncio
import traceback
import signal
import os
import sys
import websockets
from websockets.exceptions import ConnectionClosed
from csprotocol import protocol
from ssprotocol import dataHeaderDefine
import pickle
from lib.jsonhelp import classDictDumpPurePython
from connect.proc import procVariable
from optparse import OptionParser
from lib import fifoMgr,onlineMgr,reciveMgr
from lib.pubSub import subMgr
from connect import connect_config
from config import zoneConfig
from error.errorCode import exceptionLogic,errorLogic
from lib import clientSerialiser
import uuid
import uvloop
import json
from lib.timehelp import timeHelp


g_obj_loop = asyncio.get_event_loop()

g_dic_onlineFD = {}

g_obj_websocket = None


@asyncio.coroutine
def __secTickCallLater():

    #TODO 在线用户量日志
    # 日志
    dictOnline = {
        'billType': 'onlineBill',
        'groupId': groupid,
        'onlineCount': len(g_dic_onlineFD),

    }
    logging.getLogger('bill').info(json.dumps(dictOnline))
    try:
        g_obj_loop.call_later(10, lambda: asyncio.async(__secTickCallLater()))
    except Exception as e:
        logging.error('{}, {}'.format(timeHelp.getNow(), traceback.format_exc()))
    logging.info("ticket the service")

@asyncio.coroutine
def handlerPushMessage(head_message,body_message):
    global g_dic_onlineFD

    try:

        logging.debug("broad onlineClient num [{}]".format(len(g_dic_onlineFD)))

        #安全检查
        objSSHead = head_message
        if objSSHead.iBroadCast == 1:

            respHead = protocol.PC_msgHead()
            respHead.msgId = objSSHead.strMsgId

            pc_body_class = body_message
            body_dict = classDictDumpPurePython.class2ProtoDict(pc_body_class)
            #print(body_dict)
            dictSend = {"head": respHead.__dict__, "body": body_dict}

            bytesSend = clientSerialiser.dumps(procVariable.debug,dictSend)

            logging.debug("broad cast the message [{}] [{}]".format(objSSHead.strMsgId,dictSend))

            listDeleteWs = []
            for client_fd, objWs in g_dic_onlineFD.items():

                if objWs is None:
                    logging.error("ws disconnnect objWs is None fd{}".format(client_fd))
                    return
                else:
                    if not objWs.open:
                        logging.error("ws disconnnect state")
                        #g_dic_onlineFD.pop(client_fd)
                        listDeleteWs.append(client_fd)

                try:
                    yield from objWs.send(bytesSend)
                except Exception as e:
                    logging.exception(e)
                    yield from objWs.close()

            for var_delete_id in listDeleteWs:
                g_dic_onlineFD.pop(var_delete_id, None)

        else:
            #push 给某个用户
            #objSSHead.strClientUdid 是logic 构造的，不准确，由connect 这边存这个索引
            objWs = g_dic_onlineFD.get(objSSHead.strClientUdid, None)
            if objWs is None or not objWs.open:
                logging.error("push ws disconnnect account[{}]".format(objSSHead.strClientUdid))
                #g_dic_onlineFD.pop(objSSHead.strClientUdid)
            else:

                respHead = protocol.PC_msgHead()
                respHead.msgId = objSSHead.strMsgId

                pc_body_class = body_message
                body_dict = classDictDumpPurePython.class2ProtoDict(pc_body_class)

                dictSend = {"head": respHead.__dict__, "body": body_dict}
                bytesSend = clientSerialiser.dumps(procVariable.debug,dictSend)

                logging.debug("push the message [{}] to account[{}] [{}]".format(objSSHead.strMsgId,objSSHead.strAccountId,dictSend))
                #print(body_dict)
                try:
                    yield from objWs.send(bytesSend)
                except Exception as e:
                    logging.exception(e)
                    yield from objWs.close()

    except:
        logging.error(traceback.format_exc())

@asyncio.coroutine
def handlerLogicMessage(head_message,body_message):
    global  g_dic_onlineFD

    try:
        #print("handlerLogicMessage {} {}".format(head_message,body_message))

        #安全检查
        objSSHead = head_message

        if objSSHead.iBroadCast == 0:

            objWs = g_dic_onlineFD.get(objSSHead.strClientUdid, None)

            if objWs is None:
                logging.error("ws disconnnect objWs is None Udid{}".format(objSSHead.strClientUdid))
                return
            else:
                if not objWs.open:
                    logging.error("ws disconnnect state")
                    g_dic_onlineFD.pop(objSSHead.strClientUdid)

            respHead = protocol.PC_msgHead()
            respHead.msgId = objSSHead.strMsgId
            pc_body_class = body_message
            body_dict = classDictDumpPurePython.class2ProtoDict(pc_body_class)
            dictSend = {"head":respHead.__dict__,"body":body_dict}
            #print(body_dict)
            bytesSend = clientSerialiser.dumps(procVariable.debug,dictSend)

            yield from objWs.send(bytesSend)
        else:
            logging.error("invalid get broadcast message")

        if objSSHead.iInnerId != 0:
            pass


    except:
        logging.error(traceback.format_exc())

@asyncio.coroutine
def handlerWebSocket(websocket, path):
    global g_dic_onlineFD

    #strThisAccountId = ""
    strThisUdid = str(uuid.uuid4())

    g_dic_onlineFD[strThisUdid] = websocket

    while True:
        try:
            bytesBuff = yield from websocket.recv()

            try:
                if bytesBuff is not None:
                    #TODO safe check
                    if len(bytesBuff) <= 0:
                        return

                    msgDict = clientSerialiser.loads(procVariable.debug,bytesBuff)

                    objSSHeader =  dataHeaderDefine.classSSHead()

                    objSSHeader.strMsgId = msgDict['head']['msgId']
                    objSSHeader.strAccountId = msgDict['head']['accountId']
                    objSSHeader.strClientUdid = strThisUdid
                    objSSHeader.strClientIp = websocket.remote_address[0]
                    objSSHeader.iClientPort = websocket.remote_address[1]
                    objSSHeader.strToken = msgDict['head']['token']

                    if objSSHeader.strMsgId == protocol.connect:
                        if len(objSSHeader.strAccountId) > 0:

                            #设置在线信息,如果是新连接,回发消息过来
                            yield from onlineMgr.classOnlineMgr.getInstance().setOnlineClient(objSSHeader.strAccountId,
                                                                                       procVariable.group_id,
                                                                                       procVariable.host,
                                                                                       strThisUdid)

                            dictSend = {"head": msgDict['head'], "body": {"ret":0,"reDes":""}}
                            # print(body_dict)
                            bytesSend = clientSerialiser.dumps(procVariable.debug, dictSend)
                            yield from websocket.send(bytesSend)

                        continue



                    logging.debug("recive msg [{}] ip[{}]".format(objSSHeader.strMsgId,objSSHeader.strClientIp))

                    #strThisAccountId = objSSHeader.strAccountId
                    bytesSSHead = pickle.dumps(objSSHeader)
                    bytesBody = pickle.dumps(msgDict['body'])

                    yield from fifoMgr.classFIFOMgr.getInstance().publish(bytesSSHead,bytesBody)

                else:
                    #TODO logging.error()
                    pass
            except Exception as inner:
                logging.error(repr(inner))

        except exceptionLogic as e:
            logging.error(repr(e))


        except ConnectionClosed as e:

            if strThisUdid != "":
                if strThisUdid in g_dic_onlineFD:
                    g_dic_onlineFD.pop(strThisUdid)

            logging.exception(e)
            #yield from websocket.close()
            #asyncio.Task.current_task().cancel()
            return
        except:
            return

def __initLog():
    log.initLogger(os.path.dirname(os.path.realpath(__file__)) + "/../logdata/","connect_svr",connect_config.log_level,procVariable.debug)
    log.initLogger(os.path.dirname(os.path.realpath(__file__)) + "/../logdata/", "bill", logging.DEBUG)

@asyncio.coroutine
def __initFiFo():

    if procVariable.debug:
        fifoMgr.classFIFOMgr(connect_config.connect2logic_queue_key.format(procVariable.group_id),
                                                                    connect_config.logic2connect_queue_key.format(procVariable.group_id),
                                                                    zoneConfig.redis_address_for_local,
                                                                    zoneConfig.redis_pwd,
                                                                    zoneConfig.redis_fifo_db,
                                                                    g_obj_loop, 2, 2)
    else:
        fifoMgr.classFIFOMgr(connect_config.connect2logic_queue_key.format(procVariable.group_id),
                                                                    connect_config.logic2connect_queue_key.format(procVariable.group_id),
                                                                    zoneConfig.redis_address_for_local,
                                                                    zoneConfig.redis_pwd,
                                                                    zoneConfig.redis_fifo_db,
                                                                    g_obj_loop)


    yield from fifoMgr.classFIFOMgr.getInstance().connectRedis()

    fifoMgr.classFIFOMgr.getInstance().registerCall(handlerLogicMessage)
    fifoMgr.classFIFOMgr.getInstance().bDebug = procVariable.debug



@asyncio.coroutine
def __initOnline():

    if procVariable.debug:
        onlineMgr.classOnlineMgr(connect_config.redis_online_config_debug,
                                                                    g_obj_loop,2,2)
    else:
        onlineMgr.classOnlineMgr(connect_config.redis_online_config,
                                                                    g_obj_loop)

    yield from onlineMgr.classOnlineMgr.getInstance().connectRedis()

@asyncio.coroutine
def __initPubSub():

    if procVariable.debug:
        subMgr.classSubMgr(connect_config.all2connect_broadcast_queue_key,
            connect_config.redis_debug_address_for_push,
            connect_config.redis_pwd,
            connect_config.redis_push_db,
            g_obj_loop)
    else:
        subMgr.classSubMgr(connect_config.all2connect_broadcast_queue_key,
            connect_config.redis_address_for_push,
            connect_config.redis_pwd,
            connect_config.redis_push_db,
            g_obj_loop)

    subMgr.classSubMgr.getInstance().registerCall(handlerPushMessage)
    yield from subMgr.classSubMgr.getInstance().connectRedis()

@asyncio.coroutine
def __initReciveMgr():

    if procVariable.debug:
        reciveMgr.classReciveMgr(
            connect_config.redis_push_config_debug,
            g_obj_loop,2,2)
    else:
        reciveMgr.classReciveMgr(
            connect_config.redis_push_config,
            g_obj_loop)

    reciveMgr.classReciveMgr.getInstance().registerCall(handlerPushMessage)
    yield from reciveMgr.classReciveMgr.getInstance().connectRedis()


@asyncio.coroutine
def __initUpdate():

    global g_obj_websocket

    asyncio.ensure_future(g_obj_websocket)
    #asyncio.ensure_future(singletonDefine.g_obj_websocketForSsl)
    asyncio.ensure_future(fifoMgr.classFIFOMgr.getInstance().updateFifoChannel())
    #asyncio.ensure_future(singletonDefine.g_obj_fifoMgr.updatePushChannel())
    asyncio.ensure_future(subMgr.classSubMgr.getInstance().updatePubSubChannel())
    asyncio.ensure_future(reciveMgr.classReciveMgr.getInstance().updatePushData(procVariable.host,procVariable.group_id))
    asyncio.ensure_future(__secTickCallLater())

@asyncio.coroutine
def __initWebsocket():

    global g_obj_websocket
    #import ssl
    #sc = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    #sc.load_cert_chain('./ca/214534900800071.pem', './ca/214534900800071.key')

    g_obj_websocket = websockets.serve(handlerWebSocket, host=procVariable.websocket_ip, port=int(procVariable.websocket_port),
                                                       timeout=2, max_queue=2 ** 10)
    print(type(g_obj_websocket))

    #singletonDefine.g_obj_websocketForSsl = websockets.serve(handlerWebSocket, host=procVariable.websocket_ip, port=443,
    #                                                         ssl=sc, timeout=2, max_queue=2 ** 10)
    #print(type(singletonDefine.g_obj_websocketForSsl))

def __stopServer():
    pass


@asyncio.coroutine
def init():
    try:
        g_obj_loop.set_debug(procVariable.debug)
        print("aioevent is {} modle".format(g_obj_loop.get_debug()))

        logging.getLogger('asyncio').setLevel(connect_config.async_log_level)
        logging.getLogger('aioredis').setLevel(connect_config.redis_log_level)
        logging.getLogger('websockets.protocol').setLevel(connect_config.websocket_log_level)
        logging.getLogger('websockets.server').setLevel(connect_config.websocket_log_level)#connect_config.websocket_log_level)

        __initLog()
        print("init fifo")
        yield from __initFiFo()

        print("init online")
        yield from __initOnline()
        print("init pubsub")
        yield from __initPubSub()
        print("init reciveMgr")
        yield from __initReciveMgr()

        yield from asyncio.sleep(0.5)
        print("init websockt")
        yield from __initWebsocket()

        yield from asyncio.sleep(0.5)
        print("init update")
        yield from __initUpdate()
        #g_obj_loop.call_later(0.1,lambda: asyncio.async(__secTickCallLater()))

        sys.stdout.write("-----> All modules start up successfully! <-----")
        sys.stdout.flush()

    except:
        exit(0)


if "__main__" == __name__:

    if sys.version_info[0] < 3:
        print("Found Python interpreter less 3.0 version not support: %s \n"%sys.version)
        sys.exit()
    else:
        parser = OptionParser(usage="%prog --rf <runFlag> --wid <workid> --wip <websocketip> --wp <websocketport>", version="%prog 0.3")
        parser.add_option("--rf", "--runFlag", dest="runFlag", help="runFlag debug or release")
        parser.add_option("--wid", "--workid", dest="workid", help="workid 1 ~ N")
        parser.add_option("--gid", "--groupid", dest="groupid", help="groupid 1 ~ N")
        parser.add_option("--wip", "--websocketip",dest="websocketip",help="websocketip")
        parser.add_option("--wp", "--websocketport",dest="websocketport",help="websocketport")
        parser.add_option("--gdb", "--gdb", dest="gdb", help="gdb")
        parser.add_option("--host", "--host", dest="host", help="host")

        (options, args) = parser.parse_args()

        runFlag = str(options.runFlag)
        workid = str(options.workid)
        groupid = str(options.groupid)
        if options.websocketip is None:
            websocketip = "0.0.0.0"
        else:
            websocketip = str(options.websocketip)

        websocketport = str(options.websocketport)
        gdb = str(options.gdb)
        host = str(options.host)

        if gdb == "gdb":
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
        except:
            print("work_id not valid please --help the detail")
            exit(0)

        procVariable.websocket_ip = websocketip
        procVariable.websocket_port = websocketport

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
        subMgr.classSubMgr.getInstance().stop()
        g_obj_loop.stop()
        g_obj_loop.run_forever()
    except:
        logging.error(traceback.format_exc())

    finally:
        g_obj_loop.close()