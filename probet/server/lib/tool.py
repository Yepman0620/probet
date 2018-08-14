import base64
import hmac
from datawrapper.dataBaseMgr import classDataBaseMgr
import logging
from functools import wraps
from lib.timehelp import timeHelp
from error.errorCode import errorLogic, exceptionLogic
from appweb.proc import procVariable


def certify_token(key, token):
    try:
        token_str = base64.urlsafe_b64decode(token).decode('utf-8')
        token_list = token_str.split(':')
        if len(token_list) != 2:
            raise exceptionLogic(errorLogic.login_token_not_valid)
        ts_str = token_list[0]
        if int(float(ts_str)) < timeHelp.getNow():
            raise exceptionLogic(errorLogic.login_token_expired)
        known_sha1_tsstr = token_list[1]
        sha1 = hmac.new(key.encode("utf-8"), ts_str.encode('utf-8'), 'sha1')
        calc_sha1_tsstr = sha1.hexdigest()
        if calc_sha1_tsstr != known_sha1_tsstr:
            # token certification failed
            raise exceptionLogic(errorLogic.login_token_not_valid)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.player_token_certify_not_success)


def user_token_required(view_func):
    """token校验装饰器
    :param func:函数名
    :return: 闭包函数名
    """

    @wraps(view_func)
    def wrapper(*args, **kwargs):

        if not procVariable.debug:
            #debug 模式不验证token
            accountId = args[0].get('accountId', '')
            token = args[0].get('token', '')
            source = args[0].get('source', 'pc')
            if not all([accountId, token, source]):
                logging.debug(errorLogic.client_param_invalid)
                raise exceptionLogic(errorLogic.client_param_invalid)

            if len(accountId) <= 0:
                raise exceptionLogic(errorLogic.player_id_empty)

            objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(accountId)
            if not objPlayerData:
                logging.debug(errorLogic.player_data_not_found)
                raise exceptionLogic(errorLogic.player_data_not_found)

            certify_token(accountId, token)

            if source == 'pc':
                if token != objPlayerData.strToken and procVariable.debug:
                    raise exceptionLogic(errorLogic.login_token_not_valid)
            elif source == 'app':
                if token != objPlayerData.strAppToken:
                    raise exceptionLogic(errorLogic.login_token_not_valid)
            else:
                raise exceptionLogic(errorLogic.login_token_not_valid)

        a = yield from view_func(*args, **kwargs)
        return a

    return wrapper


def agent_token_required(view_func):
    """token校验装饰器
    :param func:函数名
    :return: 闭包函数名
    """

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        agentId = args[0].get('agentId', '')
        token = args[0].get('token', '')
        source = args[0].get('source', 'pc')
        if not all([agentId, token, source]):
            logging.exception(errorLogic.client_param_invalid)
            raise exceptionLogic(errorLogic.client_param_invalid)
        certify_token(agentId, token)
        objPlayerData = yield from classDataBaseMgr.getInstance().getPlayerData(agentId)
        objAgentData = yield from classDataBaseMgr.getInstance().getAgentData(agentId)
        if objPlayerData is None:
            raise exceptionLogic(errorLogic.player_data_not_found)
        if objPlayerData.iUserType != 2:
            raise exceptionLogic(errorLogic.agent_data_not_found)
        if source == 'pc':
            if token != objAgentData.strToken:
                raise exceptionLogic(errorLogic.login_token_not_valid)
        elif source == 'app':
            if token != objAgentData.strAppToken:
                raise exceptionLogic(errorLogic.login_token_not_valid)
        else:
            raise exceptionLogic(errorLogic.login_token_not_valid)
        a = yield from view_func(*args, **kwargs)
        return a

    return wrapper
