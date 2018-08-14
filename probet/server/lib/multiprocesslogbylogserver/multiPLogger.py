import os
import logging
import logging.handlers


strDefaultFormatter = '%(asctime)s|%(levelname)s|%(filename)s:%(lineno)d|%(funcName)s|%(message)s'
strBillFormatter = '%(asctime)s|%(message)s'

def __initLogger(level:int,path:str,logger:str,filePath:str):

    if logger == "bill":
        objFormatter = logging.Formatter(strBillFormatter)
    else:
        objFormatter = logging.Formatter(strDefaultFormatter)

    objLogger = logging.getLogger(logger)

    objTcpHandler = logging.handlers.SocketHandler("127.0.0.1",20001)
    try:
        objTcpHandler.makeSocket()
        print("socket logger")
    except OSError as e:
        # loggerserver 没有打开,或者有问题
        # 用本地的 日志handler
        objTcpHandler = logging.handlers.TimedRotatingFileHandler(path + filePath,
                                                                 # maxBytes = 1024 * 1024 * 256,
                                                                 backupCount=9,
                                                                 when='MIDNIGHT',
                                                                 delay=True,
                                                                 encoding = "utf-8")
        print("local logger")

    objTcpHandler.setFormatter(objFormatter)

    objLogger.addHandler(objTcpHandler)
    objLogger.setLevel(level)

    objLogger.propagate = False

    #root logger
    objRootLogger = logging.getLogger()
    objRootLogger.setLevel(level)

    return objLogger


def initLogger(level:int,path:str,logger:str=None,filePath:str="",editor=True):

    if not os.path.exists(os.path.dirname(path)):
        print(os.path.dirname(path))
        os.mkdir(os.path.dirname(path))

    objLogger = __initLogger(level,path,logger,filePath)
    if editor:
        objFormatter = logging.Formatter(strDefaultFormatter)
        objConsoleHandler = logging.StreamHandler()
        objConsoleHandler.setFormatter(objFormatter)
        objLogger.addHandler(objConsoleHandler)
