# 短信、邮件验证码的redis有效期, 单位：秒
SMS_CODE_REDIS_EXPIRES = 300

# 后台查询所有消息的分页，每页显示的数量
MSG_PAGE_COUNT = 10

# 登陆Token的有效期, 单位：秒
LOGIN_TOKEN_EXPIRES = 86400 * 30

# 转账的钱包列表
WALLET_LIST = ["中心钱包", "平博钱包"]  #  "电竞钱包"

# 存款方式列表

# DEPOSIT_LIST = [{"name": "支付宝扫码", "value": ["线路一", "线路二"], "desc": "AlipayCode"},
#                 {"name": "微信扫码", "value": ["线路一"], "desc": "WeXinCode"},
#                 {"name": "银联扫码", "value": [], "desc": "UnionpayCode"},
#                 {"name": "QQ支付扫码", "value": ["线路一", "线路二"], "desc": "QQpayCode"},
#                 {"name": "银行卡转账", "value": [], "desc": "BankTransfer"},
#                 {"name": "支付宝转账", "value": [], "desc": "AlipayTransfer"},
#                 {"name": "微信转账", "value": [], "desc": "WeixinTransfer"},
#                 ,]

DEPOSIT_LIST = [{"name": "银行卡转账", "value": [], "desc": "BankTransfer"},
                {"name": "支付宝转账", "value": [], "desc": "AlipayTransfer"},
                {"name": "微信转账",   "value": [], "desc": "WeixinTransfer"},

                {"name": "银联快捷",   "value": [
                                            {"channel": "线路一", "channelName":"lpay","payMin":100,"payMax": 20000},
                                            {"channel": "线路二", "channelName":"xgx","payMin": 100,"payMax": 49999}],"desc": "QuickPay"},

                {"name": "QQ支付扫码", "value": [
                                            {"channel": "线路一", "channelName":"lpay","payMin":100,"payMax": 1000},
                                            {"channel": "线路二", "channelName":"xgx","payMin": 100,"payMax": 49999}], "desc": "QQpayCode"},
                {"name": "支付宝扫码", "value": [
                                            {"channel": "线路一", "channelName":"xgx","payMin": 100,"payMax": 5000}], "desc": "AlipayCode"},

                {"name": "微信扫码",   "value": [
                                            {"channel":"线路一", "channelName":"lpay","payMin":1,"payMax": 300}], "desc": "WeiXinCode"},]

# 银联支付档次
THIRD_PAY_GRADE = [100, 500, 1000, 2000, 5000]

# 其他第三方支付档次
OTHER_THIRD_PAY_GRADE = [100, 200, 500, 1000, 2000]

# 银行列表
BANK_LIST = [{"name": "工商银行", "value": "ICBC"}, {"name": "建设银行", "value": "CCB"},
             {"name": "中国银行", "value": "BOC"}, {"name": "招商银行", "value": "CMB"},
             {"name": "农业银行", "value": "ABC"}, {"name": "交通银行", "value": "BOCOM"},
             {"name": "民生银行", "value": "CMBC"}, {"name": "广发银行", "value": "CGB"},
             {"name": "浦发银行", "value": "SPDB"}, ]

# 存款费率名
RATE_LIST = ['银行卡转账', '支付宝转账', '微信转账', '支付宝扫码', 'QQ扫码', '银联扫码']

#沙巴api_url
shaba_url="http://tsa.domain.com/api"