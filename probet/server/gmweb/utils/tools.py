import base64
import hmac
import json
import aiohttp
from sqlalchemy import select
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.models import *
import logging
import time
from functools import wraps
import asyncio
from error.errorCode import errorLogic, exceptionLogic

def certify_admin_token(key, token):
    try:
        token_str = base64.urlsafe_b64decode(token).decode('utf-8')
        token_list = token_str.split(':')
        if len(token_list) != 2:
            return False
        ts_str = token_list[0]
        if float(ts_str) < time.time():
            return False

        known_sha1_tsstr = token_list[1]
        sha1 = hmac.new(key.encode("utf-8"), ts_str.encode('utf-8'), 'sha1')
        calc_sha1_tsstr = sha1.hexdigest()
        if calc_sha1_tsstr != known_sha1_tsstr:
            return False

        return True
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.player_token_certify_not_success)

def token_required(view_func):
    """token校验装饰器
    :param func:函数名
    :return: 闭包函数名
    """
    @wraps(view_func)
    def wrapper(*args,**kwargs):
        conn = classSqlBaseMgr.getInstance()
        accountId=args[0].get('accountId','')
        token=args[0].get('token','')
        if not all([accountId,token]):
            logging.debug(errorLogic.client_param_invalid)
            raise exceptionLogic(errorLogic.client_param_invalid)
        try:
            sql=select([tb_admin]).where(tb_admin.c.accountId==accountId)
            listRest=yield from conn._exeCute(sql)
            account=yield from listRest.fetchone()
        except Exception as e :
            logging.debug(e)
            raise exceptionLogic(errorLogic.db_error)

        if not account:
            logging.debug(errorLogic.wrong_accountId_or_password)
            raise exceptionLogic(errorLogic.wrong_accountId_or_password)

        if account['token']!=token:
            logging.debug(errorLogic.token_not_valid)
            raise exceptionLogic(errorLogic.token_not_valid)
        is_pass=certify_admin_token(accountId,token)

        if not is_pass:
            #用户未登录
            logging.debug(errorLogic.token_not_valid)
            raise exceptionLogic(errorLogic.token_not_valid)
        args[0]['account'] = account
        a= yield from view_func(*args,**kwargs)
        return a
    return wrapper


def get_permission(accountId):
    # 获取该用户的权限名
    try:
        conn = classSqlBaseMgr.getInstance()
        sql=select([tb_admin]).where(tb_admin.c.accountId==accountId)
        listRest=yield from conn._exeCute(sql)
        user=yield from listRest.fetchone()
        if not user:
            logging.debug(errorLogic.player_data_not_found)
            raise exceptionLogic(errorLogic.player_data_not_found)

        if not user['role_id']:
            logging.debug(errorLogic.player_data_not_found)
            raise exceptionLogic(errorLogic.player_data_not_found)

        sql = "SELECT dj_admin_action.action_name FROM dj_admin_action WHERE dj_admin_action.id IN (SELECT dj_admin_role_action.action_id FROM dj_admin_role_action WHERE dj_admin_role_action.role_id ={})".format(user['role_id'])
        listRest = yield from conn._exeCute(sql)
        objNames = yield from listRest.fetchall()
        action_names = []
        for x in objNames:
            action_names.append(x['action_name'])

        return  action_names
    except Exception as e :
        logging.debug(e)
        raise exceptionLogic(errorLogic.db_error)


# 权限校验装饰器
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            accountId = args[0].get('accountId', '')
            permissions=yield from get_permission(accountId)
            if permission in permissions:
                a = yield from f(*args, **kwargs)
                return a
            else:
                logging.debug(errorLogic.user_permission_denied)
                raise exceptionLogic(errorLogic.user_permission_denied)

        return decorated_function
    return decorator

#淘宝ip地址查询api
@asyncio.coroutine
def getAddressByIp(ip:str):
    url="http://ip.taobao.com/service/getIpInfo.php"
    params={}
    params['ip']=ip
    try:
        with (aiohttp.ClientSession()) as session:
            with aiohttp.Timeout(10):
                resp=yield from session.get(url=url,params=params)
                if resp.status!=200:
                    logging.debug(errorLogic.third_party_error)
                    raise exceptionLogic(errorLogic.third_party_error)
                res = yield from resp.read()
                res = json.loads(res.decode())
                code = res.get('code', '')
                if code != 0:
                    logging.debug(errorLogic.third_party_error)
                    raise exceptionLogic(errorLogic.third_party_error)
                return "{},{}".format(res['data']['region'],res['data']['city'])
    except Exception as e:
        raise e

#{"code":0,"data":{"ip":"119.137.54.13","country":"中国","area":"","region":"广东","city":"深圳","county":"XX","isp":"电信","country_id":"CN","area_id":"","region_id":"440000","city_id":"440300","county_id":"xx","isp_id":"100017"}}