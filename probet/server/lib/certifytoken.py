from lib.timehelp import timeHelp
import base64
import hmac
import logging
from datawrapper.dataBaseMgr import classDataBaseMgr
from error.errorCode import exceptionLogic,errorLogic



def certify_token(key, token):
    try:
        token_str = base64.urlsafe_b64decode(token).decode('utf-8')
        token_list = token_str.split(':')
        if len(token_list) != 2:
            raise exceptionLogic(errorLogic.login_token_not_valid)
        ts_str = token_list[0]
        if int(float(ts_str)) < timeHelp.getNow():
            # return False
            raise exceptionLogic(errorLogic.login_token_expired)
        known_sha1_tsstr = token_list[1]
        sha1 = hmac.new(key.encode("utf-8"), ts_str.encode('utf-8'), 'sha1')
        calc_sha1_tsstr = sha1.hexdigest()
        if calc_sha1_tsstr != known_sha1_tsstr:
            # token certification failed
            # return False
            raise exceptionLogic(errorLogic.login_token_not_valid)
        # token certification success
        # return True
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.player_token_certify_not_success)

