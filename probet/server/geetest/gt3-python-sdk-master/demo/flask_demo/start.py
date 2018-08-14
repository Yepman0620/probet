#coding:utf-8
import json
import random
from functools import wraps
import redis
import logging
from flask import session, make_response, Flask, request, render_template
from sdk.geetest import GeetestLib
from flask_cors import *

#请在官网申请ID使用，示例ID不可使用
pc_geetest_id = '9eeb45ec7c4b0c30b941a128fabdf220'
pc_geetest_key = '0be06ba9881243a6cebab685df2c8bb0'
mobile_geetest_id = "9eeb45ec7c4b0c30b941a128fabdf220"
mobile_geetest_key = "0be06ba9881243a6cebab685df2c8bb0"
app = Flask(__name__)
app.config.update(
    DEBUG=True,
)
CORS(app, supports_credentials=True)
# redis的改成指定的ip
redisclienet = redis.StrictRedis(host='127.0.0.1', port=6379, db=1, password='baobaobuku')


def allow_cross_domain(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        rst.headers['Access-Control-Allow-Origin'] = '*'
        rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        allow_headers = "Referer,Accept,Origin,User-Agent,x-requested-with,content-type"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        return rst
    return wrapper_fun


@app.route('/pc-geetest/register', methods=["GET"])
@allow_cross_domain
def get_pc_captcha():
    """初始化，生成验证码"""
    user_id = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    len_chars = len(chars) - 1
    for i in range(4):
        user_id += chars[random.randint(0, len_chars)]
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    # session[gt.GT_STATUS_SESSION_KEY] = status
    # session["user_id"] = user_id
    redisclienet.setex(gt.GT_STATUS_SESSION_KEY, 300, status)
    redisclienet.setex("user_id", 300, user_id)
    response_str = gt.get_response_str()

    return response_str


@app.route('/pc-geetest/validate', methods=["POST"])
@allow_cross_domain
def pc_validate_captcha():
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    challenge = request.get_json()[gt.FN_CHALLENGE]
    validate = request.get_json()[gt.FN_VALIDATE]
    seccode = request.get_json()[gt.FN_SECCODE]
    # status = session[gt.GT_STATUS_SESSION_KEY]
    # user_id = session["user_id"]
    status = redisclienet.get(gt.GT_STATUS_SESSION_KEY)
    user_id = redisclienet.get("user_id")
    if status:
        result = gt.success_validate(challenge, validate, seccode, user_id)
    else:
        result = gt.failback_validate(challenge, validate, seccode)
        logging.error(repr(result))
    result = '{"ret": 0}' if result else '{"ret": 0}'
    return result


@app.route('/pc-geetest/ajax_validate', methods=["POST"])
@allow_cross_domain
def pc_ajax_validate():
    """验证拖动结果"""
    gt = GeetestLib(pc_geetest_id,pc_geetest_key)
    challenge = request.get_json()[gt.FN_CHALLENGE]
    validate = request.get_json()[gt.FN_VALIDATE]
    seccode = request.get_json()[gt.FN_SECCODE]
    # status = session[gt.GT_STATUS_SESSION_KEY]
    # user_id = session["user_id"]
    status = redisclienet.get(gt.GT_STATUS_SESSION_KEY)
    user_id = redisclienet.get("user_id")
    if status:
        result = gt.success_validate(challenge, validate, seccode, user_id, data='', userinfo='')
    else:
        result = gt.failback_validate(challenge, validate, seccode)
        logging.error(repr(result))
    result = {"status": "success"} if result else {"status": "fail"}
    return json.dumps(result)


@app.route('/mobile-geetest/register', methods=["GET"])
@allow_cross_domain
def get_mobile_captcha():
    user_id = 'test'
    gt = GeetestLib(mobile_geetest_id, mobile_geetest_key)
    status = gt.pre_process(user_id)
    # session[gt.GT_STATUS_SESSION_KEY] = status
    # session["user_id"] = user_id
    redisclienet.setex(gt.GT_STATUS_SESSION_KEY, 300, status)
    redisclienet.setex("user_id", 300, user_id)
    response_str = gt.get_response_str()
    return response_str


@app.route('/mobile-geetest/ajax_validate', methods=["POST"])
@allow_cross_domain
def mobile_ajax_validate():
    gt = GeetestLib(mobile_geetest_id,mobile_geetest_key)
    challenge = request.get_json()[gt.FN_CHALLENGE]
    validate = request.get_json()[gt.FN_VALIDATE]
    seccode = request.get_json()[gt.FN_SECCODE]
    # status = session[gt.GT_STATUS_SESSION_KEY]
    # user_id = session["user_id"]
    status = redisclienet.get(gt.GT_STATUS_SESSION_KEY)
    user_id = redisclienet.get("user_id")
    if status:
        result = gt.success_validate(challenge, validate, seccode, user_id,data='',userinfo='')
    else:
        result = gt.failback_validate(challenge, validate, seccode)
        logging.error(repr(result))
    result = {"status":"success"} if result else {"status":"fail"}
    return json.dumps(result)

@app.route('/')
def login():
    return render_template('login.html')


if __name__ == '__main__':
    app.secret_key = 'i-like-python-nmba'
    app.run(host='0.0.0.0', port=5000)  # 启动时改成相应的ip、port

