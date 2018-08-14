import asyncio
import sys
import uvloop
from optparse import  OptionParser
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from appweb import appweb_config


@asyncio.coroutine
def __initLogicDataMgr():

    classDataBaseMgr(appweb_config.redis_config, g_obj_loop,False,1,1)

    yield from classDataBaseMgr.getInstance().connectRedis()
    yield from classDataBaseMgr.getInstance().loadRedisLuaScript()


    classSqlBaseMgr()
    yield from classSqlBaseMgr.getInstance().connetSql(appweb_config.mysqlAddress, 3306,
                                                           'root', appweb_config.mysqlPwd, 'probet_data',
                                                           g_obj_loop)


@asyncio.coroutine
def getPlayerDataFromRedis(strAccountId):

    objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerDataByLock(strAccountId)
    if objPlayerData is None:
        print(objPlayerData)


@asyncio.coroutine
def init():

    g_obj_loop.set_debug(False)
    print("aioevent is {} modle".format(g_obj_loop.get_debug()))

    asyncio.ensure_future(__secTickCallLater())



if __name__ == "__main__":

    if sys.version_info[0] < 3:
        print("Found Python interpreter less 3.0 version not support: %s \n"%sys.version)
        sys.exit()
    else:
        parser = OptionParser(usage="%prog --rf <runFlag> ", version="%prog 0.3")
        parser.add_option("--rf", "--runFlag", dest="runFlag", help="runFlag debug or release")
        parser.add_option("--dns", "--dns", dest="dns", help="dns")


        (options, args) = parser.parse_args()

        runFlag = str(options.runFlag)
        g_str_dns = str(options.dns)

        if runFlag == "debug":
            pass
        else:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            g_obj_loop = asyncio.get_event_loop()
            pass

        try:
            asyncio.async(init())
            g_obj_loop.run_forever()
        except KeyboardInterrupt as e:
            print(asyncio.Task.all_tasks())
            print(asyncio.gather(*asyncio.Task.all_tasks()).cancel())
            g_obj_loop.stop()
            g_obj_loop.run_forever()
        except:
            # logging.error(traceback.format_exc())
            exit(0)
        finally:
            g_obj_loop.close()