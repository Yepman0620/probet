import os
import logging
import logging.handlers
import sys


strDefaultFormatter = '%(asctime)s|%(levelname)s|%(filename)s:%(lineno)d|%(funcName)s|%(message)s'
strBillFormatter = '%(asctime)s|%(message)s'
#strDefaultFormatter = '%(asctime)s|%(msecs)s|%(levelname)s|%(filename)s:%(lineno)d|%(funcName)s|%(message)s'

if hasattr(sys, '_getframe'):
    currentframe = lambda: sys._getframe(3)
else:
    def currentframe():
        try:
            raise Exception
        except Exception:
            return sys.exc_info()[2].tb_frame.f_bak


def my_logger_format():
    f1 = currentframe()
    line_number= 0
    file_name = ""
    func_name = ""

    if f1 is not None:
        f2 =f1.f_back
        if f2 is not None:
            while hasattr(f2, "f_code"):
                co = f2.f_code
                file_name = co.co_filename
                line_number = f2.f_lineno
                func_name = co.co_filename
                break

    return file_name,line_number,func_name



def __initLogger(loggerPath:str, loggerName:str, level:int):
    global loggerInitFlag
    loggerInitFlag = True

    if loggerName == "bill":
        objFormatter = logging.Formatter(strBillFormatter)
    else:
        objFormatter = logging.Formatter(strDefaultFormatter)

    if loggerName == 'bill':
        objLogger = logging.getLogger(loggerName)
    else:
        objLogger = logging.getLogger()

    if loggerName == 'bill':
        objRotatingHandler = logging.handlers.SocketHandler("127.0.0.1", 20001)
        try:
            objRotatingHandler.makeSocket()
            print("socket logger")
        except OSError as e:
            # loggerserver 没有打开,或者有问题
            # 用本地的 日志handler
            objRotatingHandler = logging.handlers.TimedRotatingFileHandler(loggerPath+ loggerName + '_local.log',
                                                                      # maxBytes = 1024 * 1024 * 256,
                                                                      backupCount=9,
                                                                      when='MIDNIGHT',
                                                                      delay=True,
                                                                      encoding="utf-8")
    else:
        objRotatingHandler = logging.handlers.TimedRotatingFileHandler(loggerPath + loggerName + '.log',
                                                                       when='MIDNIGHT', delay=True,
                                                                       backupCount=9,encoding="utf-8")

    objRotatingHandler.setFormatter(objFormatter)

    objLogger.addHandler(objRotatingHandler)
    objLogger.setLevel(level)
    objLogger.propagate = False
    return objLogger


def initLogger(loggerPath:str, loggerName:str,level:int,editor=True):
    '''
    global e
    global i
    global d


    e = __initLogger(loggerPath, loggerName, "error")
    i = __initLogger(loggerPath, loggerName, "info")
    d = __initLogger(loggerPath, loggerName, "debug")
    '''
    #d = __initLogger(loggerPath, loggerName)
    if not os.path.exists(loggerPath):
        os.mkdir(loggerPath)

    objLogger = __initLogger(loggerPath, loggerName, level)
    if editor:
        if loggerName == "bill":
            objFormatter = logging.Formatter(strBillFormatter)
        else:
            objFormatter = logging.Formatter(strDefaultFormatter)

        objConsoleHandler = logging.StreamHandler()
        objConsoleHandler.setFormatter(objFormatter)
        objLogger.addHandler(objConsoleHandler)

    # objLogger.info("singleLogger init finish")
#initPreLogger('./',"logging.log")

if __name__ == '__main__':
    initLogger('./',"testlogging.log",10)
    logging.error("test")

