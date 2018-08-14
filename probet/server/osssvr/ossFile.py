from pymysql.err import IntegrityError
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from lib.timehelp import timeHelp
from osssvr.proc import procVariable
from osssvr.utils.models import *
import logging
import asyncio
import json
import os

class classOssFile():
    def __init__(self):
        self.file_handle = None
        self.file_name = ""
        self.file_seek_pos = 0
        self.file_seek_pos_change_flag = False

        self.init_state = False
        self.change_continue_flag = False

        self.last_change_time = 0
        self.last_update_time = timeHelp.getNow()

    def init_file(self,file_name,file_seek_pos, last_update_time=0):
        self.file_name = file_name
        try:
            self.file_handle = open(file_name,"r")

        except OSError as e:
            self.file_handle = None
            return
        fileSize = os.stat(file_name).st_size
        if fileSize >= file_seek_pos:
            self.file_seek_pos = file_seek_pos
            if last_update_time:
                self.last_update_time = last_update_time
        else:
            self.file_seek_pos = 0
            logging.error('*** file_seek_pos is {}, but file is {}'.format(file_seek_pos, fileSize))


        if self.file_handle != None:
            self.file_handle.seek(self.file_seek_pos)

    def change_file(self,file_name,file_pos):
        try:
            self.file_name = file_name
            self.file_handle = open(file_name,"r")
            self.file_seek_pos = file_pos
            self.file_handle.seek(self.file_seek_pos)
            return True
        except OSError as e:
            self.file_handle = None
            return False

    def change_file_by_handle(self,file_name,file_handler,file_pos):
        try:
            self.file_name = file_name
            self.file_handle = file_handler
            self.file_seek_pos = file_pos
            self.file_handle.seek(self.file_seek_pos)
            return True
        except OSError as e:
            self.file_handle = None
            return False

    def try_change_file(self,file_name):
        try:
            file_handle = open(file_name,"r")
            return True,file_handle
        except OSError as e:
            return False,None

    def open_file(self,file_name,file_pos):
        try:
            self.file_name = file_name
            self.file_handle = open(file_name,"r")
            self.file_seek_pos = file_pos
            self.file_handle.seek(self.file_seek_pos)
        except OSError as e:
            self.file_handle = None

    def close_file(self):
        if self.file_handle != None:
            self.file_handle.close()
            self.file_handle = None

    def check_file_handle(self):

        if self.file_handle != None:
            return True
        else:
            try:
                self.file_handle = open(self.file_name, "r")
                self.file_handle.seek(self.file_seek_pos)
                return True

            except OSError as e:
                return False


    @asyncio.coroutine
    def statistics_log(self):
        '''
        本函数是监视 bill.log 文件，需要处理这种异常：
        如果两次调用中间隔天了，比如在 0409 00:01 时调用本函数，logserver 昨天会有部分记录无法读取，
            这时候要返回去处理昨天的记录
        :return:
        '''

        now_time = timeHelp.getNow()
        self.file_seek_pos_change_flag = False


        if not timeHelp.isSameDay(now_time,self.last_update_time) or self.change_continue_flag:
            #隔日了,需要处理一下逻辑，免的丢一些数据源
            #查看新的日志源
            #-86400 是为了拼出上一天的日志名称，如
            self.change_continue_flag = True
            newFileName = os.path.dirname(os.path.realpath(__file__)) + "/../logdata/bill.log"
            # newFileName = os.path.dirname(os.path.realpath(__file__)) + "/logdata/bill.log"

            oldFileName = newFileName + '.' +str(timeHelp.timestamp2Str(now_time - 86400,format = "%Y-%m-%d"))

            flag,file_handle= self.try_change_file(oldFileName)
            #已经看到有滚的日志了，那么可以把这个被滚过的日志读取完毕
            if flag:
                # 如果日志已经滚过了，这里需要修改成来的滚过的文件。并且读取完毕
                self.change_file_by_handle(oldFileName, file_handle,
                                           self.file_seek_pos)

                ## 处理途中如果出错了就算了，记下日志
                try:
                    yield from self.read_all_lines()
                except Exception as e:
                    #print('*** error when deal with {}: {}'.format(oldFileName, repr(e)))
                    logging.exception(e)
                #这里立即入库一下,因为lastupdatetime还没有改动到新的一天，这次的
                #file_pos_svr_id应该是隔日前一天的
                #这里要注意的问题  above
                self.close_file()

                #做个保护
                #如果日志滚上去了，但是新的日志并没有创建,但是 pos还是要归0，并记录到 mysql
                self.file_seek_pos = 0
                self.last_change_time = timeHelp.getNow()
                yield from self.file_pos_db_by_param(newFileName,0,now_time)
                self.change_continue_flag = False
                #切换到新的滚的日志handle

                while True:
                    flag, file_handle = self.try_change_file(newFileName)
                    if flag:
                        self.change_file_by_handle(newFileName,file_handle,0)
                        break
                    else:
                        #10秒一次检查是否有隔日的日志可以扫
                        yield from asyncio.sleep(10)

            elif os.path.exists(oldFileName):
                    logging.error('error: {} open file {} failed'.format(timeHelp.getNow(), oldFileName))
        else:

            yield from self.read_lines()
            if self.file_seek_pos_change_flag:
                yield from self.file_pos_db()

        self.last_update_time = now_time

    @asyncio.coroutine
    def read_lines(self):
        if not self.check_file_handle():
            return

        read_line = 999999999
        while read_line > 0:
            read_line -= 1
            line_data = self.file_handle.readline()
            if line_data != "":
                self.file_seek_pos = self.file_handle.tell()
                self.file_seek_pos_change_flag = True
                yield from self.parse_line_data(line_data)
            else:
                break

        if len(procVariable.rescanFile) <= 0:
            self.close_file()
        else:
            self.close_file()
            exit(0)

    @asyncio.coroutine
    def read_all_lines(self):
        if not self.check_file_handle():
            return

        while True:
            line_data = self.file_handle.readline()
            if line_data != "":
                self.file_seek_pos = self.file_handle.tell()
                self.file_seek_pos_change_flag = True
                yield from self.parse_line_data(line_data)
            else:
                break
        self.close_file()

    @asyncio.coroutine
    def cal_read_all_lines(self):
        if not self.check_file_handle():
            return

        while True:
            line_data = self.file_handle.readline()
            if line_data != "":
                self.file_seek_pos = self.file_handle.tell()
                self.file_seek_pos_change_flag = True
                yield from self.parse_line_data(line_data)
            else:
                break
        self.close_file()


    @asyncio.coroutine
    def parse_line_data(self,data_log_str:str):

        #print(data_log_str)
        #listLog = data_log_str.split('|')
        self.last_change_time = timeHelp.getNow()
        try:
            dictBill = json.loads(data_log_str[24:])
            billType = dictBill['billType']
            if billType  == "loginBill":
                yield from self.deal_with_login_bill(dictBill)
            elif billType == "betBill":
                yield from self.deal_with_bet_bill(dictBill)
            elif billType == "payBill":
                yield from self.deal_with_pay_bill(dictBill)
            elif billType == "regBill":
                yield from self.deal_with_reg_bill(dictBill)
            elif billType == "betResultBill":
                yield from self.deal_with_betResult_bill(dictBill)
            elif billType=="withdrawalBill":
                yield from self.deal_with_withdrawal_bill(dictBill)
            elif billType=="pingboBetResultBill":
                yield from self.deal_with_pingboBet_bill(dictBill)
            elif billType=='adminActionBill':
                yield from self.deal_with_admin_action_bill(dictBill)
            elif billType=='shabaBetBill':
                yield from self.deal_with_shaba_bet_bill(dictBill)
            elif billType == 'onlineBill':
                yield from self.deal_with_online_bill(dictBill)
            else:
                logging.error("unknown the billType[{}]".format(billType))

        except Exception as e:
            logging.exception(e)
            logging.error("seekPos[{}] not valid bill log error[{}]".format(self.file_seek_pos,repr(e)))
            logging.error(data_log_str)


    @asyncio.coroutine
    def file_pos_db(self):

        engine = classSqlBaseMgr.getInstance().getEngine()

        with (yield from engine) as conn:

            objSql = FilePos.getUpdateSqlObj(procVariable.host,self.file_name,self.file_seek_pos,self.last_change_time)
            #print(objSql)

            #print(objSql.compile().params)

            # trans = yield from conn.begin()
            # try:
            yield from conn.execute(objSql)
            # except Exception:
            #     # TODO log error
            #     yield from trans.rollback()
            # else:
            #     yield from trans.commit()

    @asyncio.coroutine
    def file_pos_db_by_param(self,file_name,file_seek_pos,last_change_time):

        engine = classSqlBaseMgr.getInstance().getEngine()

        with (yield from engine) as conn:
            objSql = FilePos.getUpdateSqlObj(procVariable.host, file_name, file_seek_pos,
                                             last_change_time)

            yield from conn.execute(objSql)



    @asyncio.coroutine
    def deal_with_login_bill(self,dictBill):
        engine = classSqlBaseMgr.getInstance().getEngine()

        with (yield from engine) as conn:
            objSql=LoginBill.getSqlObj(dictBill)
            #print(objSql)

            #print(objSql.compile().params)

            trans = yield from conn.begin()
            try:
                yield from conn.execute(objSql)
            except Exception as e:
                # TODO log error
                logging.exception(e)
                yield from trans.rollback()
            else:
                yield from trans.commit()


    @asyncio.coroutine
    def deal_with_bet_bill(self,dictBill):

        engine = classSqlBaseMgr.getInstance().getEngine()

        with (yield from engine) as conn:

            objSql = ProbetBetBill.getSqlObj(dictBill)
            #print(objSql)

            #print(objSql.compile().params)

            trans = yield from conn.begin()
            try:
                yield from conn.execute(objSql)
            except Exception as e:
                # TODO log error
                logging.exception(e)
                yield from trans.rollback()
            else:
                yield from trans.commit()

    @asyncio.coroutine
    def deal_with_pay_bill(self,dictBill):

        engine = classSqlBaseMgr.getInstance().getEngine()

        with (yield from engine) as conn:

            objSql = PayBill.getSqlObj(dictBill)
            ##print(objSql)

            ##print(objSql.compile().params)

            trans = yield from conn.begin()
            try:
                yield from conn.execute(objSql)
            except Exception as e:
                # TODO log error
                logging.exception(e)
                yield from trans.rollback()
            else:
                yield from trans.commit()

    @asyncio.coroutine
    def deal_with_admin_action_bill(self,dictBill):
        engine = classSqlBaseMgr.getInstance().getEngine()
        with(yield from engine) as conn:
            objSql=AdminActionBill.getSqlObj(dictBill)
            ##print(objSql)
            ##print(objSql.compile().params)
            trans=yield from conn.begin()
            try:
                yield from conn.execute(objSql)
            except Exception as e:
                logging.exception(e)
                yield from trans.rollback()
            else:
                yield from trans.commit()

    @asyncio.coroutine
    def deal_with_shaba_bet_bill(self, dictBill):
        engine = classSqlBaseMgr.getInstance().getEngine()
        with(yield from engine) as conn:
            objSql = ShabaBetBill.getSqlObj(dictBill)
            ##print(objSql)
            ##print(objSql.compile().params)
            trans = yield from conn.begin()
            try:
                yield from conn.execute(objSql)
            except Exception as e:
                logging.exception(e)
                yield from trans.rollback()
            else:
                yield from trans.commit()

    @asyncio.coroutine
    def deal_with_reg_bill(self, dictBill):

        engine = classSqlBaseMgr.getInstance().getEngine()

        with (yield from engine) as conn:

            objSql = RegisterBill.getSqlObj(dictBill)
            ##print(objSql)

            ##print(objSql.compile().params)

            trans = yield from conn.begin()
            try:
                yield from conn.execute(objSql)
            except Exception as e:
                # TODO log error
                logging.exception(e)
                yield from trans.rollback()
            else:
                yield from trans.commit()


    @asyncio.coroutine
    def deal_with_betResult_bill(self, dictBill):

        engine = classSqlBaseMgr.getInstance().getEngine()

        with (yield from engine) as conn:

            objSql = BetResultBill.getSqlObj(dictBill)
            ##print(objSql)

            ##print(objSql.compile().params)

            trans = yield from conn.begin()
            try:
                yield from conn.execute(objSql)
            except Exception as e:
                # TODO log error
                logging.exception(e)
                yield from trans.rollback()
            else:
                yield from trans.commit()

    @asyncio.coroutine
    def deal_with_pingboBet_bill(self, dictBill):

        engine = classSqlBaseMgr.getInstance().getEngine()

        with (yield from engine) as conn:

            objSql = PingboBetBill.getSqlObj(dictBill)
            #print(objSql)

            #print(objSql.compile().params)

            trans = yield from conn.begin()
            try:
                yield from conn.execute(objSql)
            except IntegrityError as e:
                # 如果主键重复
                logging.debug(repr(e))
                sql=PingboBetBill.getUpdateSql(dictBill)
                yield from conn.execute(sql)
                yield from trans.commit()
            except Exception as e:
                # TODO log error
                logging.exception(e)
                yield from trans.rollback()
            else:
                yield from trans.commit()


    @asyncio.coroutine
    def deal_with_withdrawal_bill(self,dictBill):
        engine=classSqlBaseMgr.getInstance().getEngine()

        with (yield from engine) as conn:

            objSql = WihtDrawalBill.getSqlObj(dictBill)
            ##print(objSql)

            ##print(objSql.compile().params)

            trans = yield from conn.begin()
            try:
                yield from conn.execute(objSql)
            except Exception as e:
                # TODO log error
                logging.exception(e)
                yield from trans.rollback()
            else:
                yield from trans.commit()

    @asyncio.coroutine
    def deal_with_online_bill(self, dictBill):
        engine = classSqlBaseMgr.getInstance().getEngine()

        with (yield from engine) as conn:

            objSql = OnlineBill.getSelectSqlObj(dictBill)
            ret = yield from conn.execute(objSql)
            if ret.rowcount<=0:
                objSql = OnlineBill.getInsertSqlObj(dictBill)
            else:
                objSql = OnlineBill.getUpdateSqlObj(dictBill)
            ##print(objSql)

            ##print(objSql.compile().params)

            trans = yield from conn.begin()
            try:
                yield from conn.execute(objSql)
            except Exception as e:
                # TODO log error
                logging.exception(e)
                yield from trans.rollback()
            else:
                yield from trans.commit()
