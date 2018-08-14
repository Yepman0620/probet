from socketserver import ThreadingTCPServer, StreamRequestHandler
import logging.handlers
import logging
import struct
import pickle
import os
import signal
import threading


LOG_BIND_PORT = 20001
filepath = os.path.dirname(os.path.realpath(__file__)) + "/../logdata/"
# filepath = os.path.dirname(os.path.realpath(__file__)) + "/logdata/"


svr = None


class LogRequestHandler(StreamRequestHandler):
    def handle(self):
        while True:
            try:
                chunk = self.connection.recv(4)
                if len(chunk) < 4:
                    break
                slen = struct.unpack(">L", chunk)[0]
                chunk = self.connection.recv(slen)
                while len(chunk) < slen:
                    chunk = chunk + self.connection.recv(slen - len(chunk))
                obj = self.unPickle(chunk)
                # 使用SocketHandler发送过来的数据包，要使用解包成为LogRecord
                # 看SocketHandler文档
                record = logging.makeLogRecord(obj)
                self.handleLogRecord(record)
            except Exception as e:
                print(repr(e))

    def unPickle(self, data):
        return pickle.loads(data)

    def handleLogRecord(self, record):
        logger = logging.getLogger(record.name)
        if (logger.hasHandlers()):
            # 如果已经注册了handlers,执行handlers
            '''
            for var_handler in logger.handlers:
                str_name = str(var_handler.__class__)
                # if str_name == "<class'logging.handlers.RotatingFileHandler'>":
                if str_name.find("RotatingFileHandler") >= 0:
                    # 如果是文件类型的日志,先关闭这个stream,以免文件不存在,会再次创建
                    # 如果不关闭,linux上,把日志删除,不会重新创建这个日志
                    # 虽然打开关闭,服务器有日志cache和日志进程,所以性能开销不大
                    var_handler.stream.close()
                    var_handler.stream = None
            '''
            logger.handle(record)
            print(repr(record))
        else:
            # 如果没有注册handlers,默认增加一个默认的handlers
            # 防止日志系统错误,丢掉了一些日志
            if record.name == "root":
                handler_unknown = logging.handlers.TimedRotatingFileHandler(filepath + 'logging' + '.log',
                                                                            backupCount=9,
                                                                            when='MIDNIGHT', delay=True)
                fmt = logging.Formatter('%(asctime)s|%(filename)s:%(lineno)d|%(funcName)s|%(process)d|%(message)s')
                addHandler(record.name, handler_unknown,fmt)

                logger.handle(record)
            elif record.name == "bill":
                handler_unknown = logging.handlers.TimedRotatingFileHandler(filepath + 'bill.log',
                                                                            backupCount=9,
                                                                            when='MIDNIGHT', delay=True)
                fmt = logging.Formatter('%(asctime)s|%(message)s')
                addHandler(record.name, handler_unknown,fmt)

                logger.handle(record)

            elif record.name == "logic":
                handler_unknown = logging.handlers.TimedRotatingFileHandler(filepath + 'logic.log',
                                                                            backupCount=9,
                                                                            when='MIDNIGHT', delay=True)
                fmt = logging.Formatter('%(asctime)s|%(levelname)s|%(filename)s:%(lineno)d|%(message)s')
                addHandler(record.name, handler_unknown, fmt)

                logger.handle(record)

            elif record.name == "result":
                handler_unknown = logging.handlers.TimedRotatingFileHandler(filepath + 'result.log',
                                                                            backupCount=9,
                                                                            when='MIDNIGHT', delay=True)
                fmt = logging.Formatter('%(asctime)s|%(levelname)s|%(filename)s:%(lineno)d|%(message)s')
                addHandler(record.name, handler_unknown, fmt)

                logger.handle(record)

            elif record.name == "notice":
                handler_unknown = logging.handlers.TimedRotatingFileHandler(filepath + 'notice.log',
                                                                            backupCount=9,
                                                                            when='MIDNIGHT', delay=True)
                fmt = logging.Formatter('%(asctime)s|%(levelname)s|%(filename)s:%(lineno)d|%(message)s')
                addHandler(record.name, handler_unknown, fmt)

                logger.handle(record)

            else:
                print("unknown record[{}]".format(record.name))

                handler_unknown = logging.handlers.TimedRotatingFileHandler(filepath + record.name + '.log',
                                                                            backupCount=9,
                                                                            when='MIDNIGHT', delay=True)
                fmt = logging.Formatter('%(asctime)s|%(filename)s:%(lineno)d|%(funcName)s|%(message)s')
                addHandler(record.name, handler_unknown, fmt)

                logger.handle(record)


def startLogSvr(bindAddress, requestHandler):
    global svr
    ThreadingTCPServer.allow_reuse_address = True
    ThreadingTCPServer.daemon_threads = True
    svr = ThreadingTCPServer(bindAddress, requestHandler)
    threading.Thread(target=svr.serve_forever).start()


def addHandler(name, handler,fmt):
    logger = logging.getLogger(name)
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False


# 先不用这个吧，用了检查 handler名字的逻辑有bug，还要继续修改,没时间改了
def memoryWapper(handler, capacity):
    hdlr = logging.handlers.MemoryHandler(capacity, target=handler)
    hdlr.setFormatter(handler.formatter)
    return hdlr


def __stop_server(param1, param2):
    # broadcast_stopserver()
    global svr
    svr.shutdown()
    svr.server_close()


def main():

    # 注册信号量,为了正常停起服,不用kill 9 的信号量来停服,不然会有可能部分逻辑不会处理完毕
    signal.signal(signal.SIGUSR1, __stop_server)

    startLogSvr(('127.0.0.1', LOG_BIND_PORT), LogRequestHandler)


if __name__ == "__main__":
    main()