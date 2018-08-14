import logging
import logging.handlers
import platform
#from lib.multiprocesslogbysyshandler.multiPocessLogHander import  MultiProcessingHandler

strDefaultFormatter = '%(asctime)s|%(levelname)s|%(filename)s:%(lineno)d|%(funcName)s|%(message)s'

#strDefaultFormatter = '%(asctime)s|%(msecs)s|%(levelname)s|%(filename)s:%(lineno)d|%(funcName)s|%(message)s'


def __initLogger(level:int,sysLocalId:int):


    objFormatter = logging.Formatter(strDefaultFormatter)
    objLogger = logging.getLogger()

    sysLogUnixSocketPath = "/dev/log"
    if platform.system() == 'Darwin':
        sysLogUnixSocketPath = "/var/run/syslog"

    objSystemHandler = logging.handlers.SysLogHandler(sysLogUnixSocketPath,
                                                      facility=sysLocalId)

    objSystemHandler.setFormatter(objFormatter)

    objLogger.addHandler(objSystemHandler)
    objLogger.setLevel(level)

    objLogger.propagate = False
    return objLogger


def initLogger(level:int,sysLocalId:int,editor=True):
    objLogger = __initLogger(level,sysLocalId)
    if editor:
        objFormatter = logging.Formatter(strDefaultFormatter)
        objConsoleHandler = logging.StreamHandler()
        objConsoleHandler.setFormatter(objFormatter)
        objLogger.addHandler(objConsoleHandler)


if __name__ == '__main__':


    print(platform.system())
    initLogger(logging.NOTSET,logging.handlers.SysLogHandler.LOG_LOCAL0)
    logging.debug("test debug")
    logging.error("test error")
    logging.info("test info")

