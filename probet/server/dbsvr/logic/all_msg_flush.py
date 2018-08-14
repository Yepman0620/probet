import asyncio
import logging
import sqlalchemy as sa
from config.zoneConfig import userConfig
from datawrapper.dataBaseMgr import classDataBaseMgr
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from lib.jsonhelp import classJsonDump
from gmweb.utils.models import Base

tbl = Base.metadata.tables["dj_all_msg"]

metadata = sa.MetaData()

@asyncio.coroutine
def doCheck(type):
    engine = classSqlBaseMgr.getInstance().getEngine()

    with (yield from engine) as conn:
        # 检查写入信息
        var_aio_redis = classDataBaseMgr.getInstance().dictAioRedis[userConfig].objAioRedis

        try:
            new_msg_list = []
            if type == 0:
                new_msg_list = yield from classDataBaseMgr.getInstance().getSysMsgNewList(var_aio_redis)
            if type == 1:
                new_msg_list = yield from classDataBaseMgr.getInstance().getNoticeMsgNewList(var_aio_redis)
            if type == 2:
                new_msg_list = yield from classDataBaseMgr.getInstance().getNewsMsgNewList(var_aio_redis)
            if type == 3:
                new_msg_list = yield from classDataBaseMgr.getInstance().getAgentMsgNewList(var_aio_redis)

            if len(new_msg_list) <= 0:
                pass
            else:
                for var_id in new_msg_list:
                    try:
                        if var_id is None:
                            logging.info(repr("无新消息"))
                            continue

                        yield from flushInsertToDb(var_id.decode(), conn, type)

                        if type == 0:
                            yield from classDataBaseMgr.getInstance().removeSysMsgNew(var_aio_redis, var_id)
                        if type == 1:
                            yield from classDataBaseMgr.getInstance().removeNoticeMsgNew(var_aio_redis, var_id)
                        if type == 2:
                            yield from classDataBaseMgr.getInstance().removeNewsMsgNew(var_aio_redis, var_id)
                        if type == 3:
                            yield from classDataBaseMgr.getInstance().removeAgentMsgNew(var_aio_redis, var_id)
                        logging.info("Save new Msg[{}]".format(var_id))
                    except Exception as e:
                        logging.error("Save new Msg exception, account=[{}], error=[{}]".format(var_id, str(e)))


        except Exception as e:
            logging.error(str(e))
        finally:
            pass

        # 检查更新信息
        try:
            dirty_msg_list = []
            if type == 0:
                dirty_msg_list = yield from classDataBaseMgr.getInstance().getSysMsgDirtyList(var_aio_redis)
            if type == 1:
                dirty_msg_list = yield from classDataBaseMgr.getInstance().getNoticeMsgDirtyList(var_aio_redis)
            if type == 2:
                dirty_msg_list = yield from classDataBaseMgr.getInstance().getNewsMsgDirtyList(var_aio_redis)
            if type == 3:
                dirty_msg_list = yield from classDataBaseMgr.getInstance().getAgentMsgDirtyList(var_aio_redis)
            if len(dirty_msg_list) <= 0:
                pass
            else:
                for var_id in dirty_msg_list:
                    try:
                        if var_id is None:
                            logging.info("Id为空")
                            continue

                        yield from flushUpdateToDb(var_id.decode(), conn, type)

                        if type == 0:
                            yield from classDataBaseMgr.getInstance().removeSysMsgDirtyList(var_aio_redis, var_id)
                        if type == 1:
                            yield from classDataBaseMgr.getInstance().removeNoticeMsgDirtyList(var_aio_redis, var_id)
                        if type == 2:
                            yield from classDataBaseMgr.getInstance().removeNewsMsgDirtyList(var_aio_redis, var_id)
                        if type == 3:
                            yield from classDataBaseMgr.getInstance().removeAgentMsgDirtyList(var_aio_redis, var_id)

                        logging.info("Save dirty Msg[{}]".format(var_id))
                    except Exception as e:
                        logging.error("Save dirty Msg exception, Msg=[{}], error=[{}]".format(var_id, str(e)))

        except Exception as e:
            logging.error(str(e))
        finally:
            pass


#########################
@asyncio.coroutine
def flushInsertToDb(msgId: str, conn, type):
    # TODO 还需要完善dataBaseMgr中的接口
    objMsg = None
    if type == 0:
        objMsg = yield from classDataBaseMgr.getInstance().getSysMsgByMsgId(msgId)
    if type == 1:
        objMsg = yield from classDataBaseMgr.getInstance().getNoticeMsgByMsgId(type, msgId)
    if type == 2:
        objMsg = yield from classDataBaseMgr.getInstance().getNewsMsgByMsgId(type, msgId)
    if type==3:
        objMsg = yield from classDataBaseMgr.getInstance().getAgentMsgByMsgId(msgId)
    if objMsg is None:
        # TODO log
        return

    sql = tbl.insert().values(
        msgId=objMsg.strMsgId,
        msgTime=objMsg.iMsgTime,
        type=objMsg.iMsgType,
        msgTitle=objMsg.strMsgTitle,
        msgDetail=objMsg.strMsgDetail,
        readFlag=objMsg.iReadFlag,
        sendTo=objMsg.strAccountId,
        sendFrom=objMsg.strSendFrom,
        broadcast=objMsg.iBroadcast,
        isdelete=objMsg.isDelete,
        # ctr=classJsonDump.dumps(objMsg.dictCTR),
    )

    trans = yield from conn.begin()
    try:
        yield from conn.execute(sql)
    except Exception as e:
        logging.error(e)
        yield from trans.rollback()
        raise e
    else:
        yield from trans.commit()


@asyncio.coroutine
def flushUpdateToDb(msgId: str, conn, type):
    # TODO 还需要完善dataBaseMgr中的接口
    objMsg = None
    if type == 0:
        objMsg = yield from classDataBaseMgr.getInstance().getSysMsgByMsgId(msgId)
    if type == 1:
        objMsg = yield from classDataBaseMgr.getInstance().getNoticeMsgByMsgId(type, msgId)
    if type == 2:
        objMsg = yield from classDataBaseMgr.getInstance().getNewsMsgByMsgId(type, msgId)
    if type == 3:
        objMsg = yield from classDataBaseMgr.getInstance().getAgentMsgByMsgId(msgId)
    if objMsg is None:
        # TODO log
        logging.info("消息为空")
        return

    sql = tbl.update().where(tbl.c.msgId == objMsg.strMsgId).values(
        msgId=objMsg.strMsgId,
        msgTime=objMsg.iMsgTime,
        type=objMsg.iMsgType,
        msgTitle=objMsg.strMsgTitle,
        msgDetail=objMsg.strMsgDetail,
        readFlag=objMsg.iReadFlag,
        sendTo=objMsg.strAccountId,
        sendFrom=objMsg.strSendFrom,
        broadcast=objMsg.iBroadcast,
        isdelete=objMsg.isDelete,
        # ctr=classJsonDump.dumps(objMsg.dictCTR),
    )
    trans = yield from conn.begin()
    try:
        yield from conn.execute(sql)
    except Exception as e:
        logging.exception(e)
        yield from trans.rollback()
        raise e
    else:
        yield from trans.commit()
