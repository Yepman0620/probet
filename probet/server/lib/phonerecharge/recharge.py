import urllib, json, hashlib, urllib3
import requests
import random


class Huafeiduo:
    # 话费多相关配置
    _gateway = 'http://api.huafeiduo.com'

    # 你的api_key
    _api_key = 'yAWZ6bOys3edJSkRrFpCMk685wnYZVCmkobepQDIHHLgoWXGqb94m41foc5dXvq8'

    # 你的secret_key
    _secret_key = 'JrbZ9FxFb9LqUxWazU5LMTR2VK5I7kFFBGuyaR4cPEsz2ezqZt2AbIrXhludvZJW'

    # 异步回调地址
    # _notify_url = 'http://yourdomain.com/callback/huafeiduo'

    def _sendRequest(self, url, params=None, method='GET', timeout=60):
        """发送HTTP请求"""
        if method.upper() == 'GET':
            return requests.request(method="get", url=url, params=params).text
        elif method.upper() == 'POST':
            return requests.post(url, data=params).text
        else:
            return ''

    def _getSign(self, params):
        """生成签名"""
        paramString = ''
        sortedKeys = sorted(params.keys())
        for k in sortedKeys:
            paramString += '%s%s' % (k, params[k])
        paramString += self._secret_key
        sign = hashlib.md5(paramString.encode("utf-8")).hexdigest()
        return sign

    def check(self, card_worth, phone_number):
        """
        检查指定面额和手机号码当前是否可以下单, 以及获取下单价格
        @param card_worth int 待检测的充值面额
        @param phone_number string 待检测的充值手机号码
        @return 检查结果为＂可以下单＂时返回数组, 此字典形如:
        {
        'price': 49.5, // 成本价
        'card_worth'=> 50, //面额
        'phone_number'=> 15623722222, //手机号码
        'area'=> '湖北武汉', //手机归属地
        'platform'=> '联通'	 //运营商
        }
        {'status': 'success', 'data': {'price': '1.3000', 'card_worth': '1', 'phone_number': '15989313006', 'area': '广东 深圳', 'platform': '移动'}}
        检查结果为"正在维护(无法充值)"时返回False
        """
        mod = 'order.phone.check'
        params = {
            'card_worth': card_worth,
            'phone_number': phone_number,
            'api_key': self._api_key
        }

        sign = self._getSign(params)

        params['sign'] = sign

        params['mod'] = mod

        ret_json_string = self._sendRequest(self._gateway, params, 'GET')

        ret = json.loads(ret_json_string)
        print("phone number check ret-------->{}".format(ret))
        try:
            if ret['status'] and ret['status'] == 'success':
                return ret['data']
        except Exception as e:
            return False

    def submit(self, card_worth, phone_number, sp_order_id):
        """
        提交充值(下单)
        注意:
        1. 提交成功不代表充值成功, 充值成功与否需要依赖异步回调结果, 或提交后调用order.phone.status接口确认订单状态
        2. 如果接口没有明确返回失败(例如请求超时),  则不能说明订单是充值失败
        @param card_worth int 充值面额
        @param phone_number string 充值手机号码
        @param sp_order_id string 商户订单号
        @return boolean 提交成功返回True, 提交失败返回False

        {'status': 'success', 'order_id': '2018020617350412539'}
        """
        mod = 'order.phone.submit'

        params = {
            'card_worth': card_worth,  # 必须  面值
            'phone_number': phone_number,  # 必须 充值号码
            # 'notify_url': self._notify_url	#可选 充值成功或失败时会向此地址发送异步回调, 以通知充值结果
            'sp_order_id': sp_order_id,
            'api_key': self._api_key
        }
        print("sp_order_id------------>{}".format(sp_order_id))
        sign = self._getSign(params)

        params['sign'] = sign

        params['mod'] = mod

        ret_json_string = self._sendRequest(self._gateway, params, 'GET')

        ret = json.loads(ret_json_string)
        print("order submit ret------------->{}".format(ret))
        if ret['status'] and ret['status'] == 'success':
            return True

        return False

    def status(self, sp_order_id):
        """
        检查当前订单状态
        @param sp_order_id string 商户订单号(同order.phone.submit接口中的sp_order_id)
        @return string:
        "init": 充值中
        "recharging": 充值中
        "success": 充值成功
        "failure": 充值失败

        {'status': 'success', 'data': {'order_status': 'success'}}
        """
        mod = 'order.phone.status'
        params = {
            'sp_order_id': sp_order_id,
            'api_key': self._api_key
        }

        sign = self._getSign(params)

        params['sign'] = sign

        params['mod'] = mod

        ret_json_string = self._sendRequest(self._gateway, params, 'GET')

        ret = json.loads(ret_json_string)
        print("order status check ret------------->{}".format(ret))
        if "status" in ret and ret['status'] == 'success':
            return ret['status']

        return False



if "__main__" == __name__:
    hfd = Huafeiduo()

    card_worth = 1  # 充值金额
    phone_number = '15989313006'  # 充值的手机号
    sp_order_id_arr = random.sample('ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', 10)  # 生成订单
    sp_order_id = ''.join(sp_order_id_arr)  # 订单ID  此订单ID用户查询订单状态
    fake_order_id = "7VJXO6DQU2"

    # check phone number    检查手机号
    ret = hfd.check(card_worth, phone_number)
    if ret is False:
        print('please retry!')

    # submit    # 提交充值
    ret = hfd.submit(card_worth, phone_number, sp_order_id)

    # check order status    # 查询订单状态
    status = hfd.status(fake_order_id)   # {'status': 'success', 'data': {'order_status': 'success'}}
    print("status--------->{}".format(status))
    if status is False:
        print('order submit fail!')
    else:
        print('order sumit success!')