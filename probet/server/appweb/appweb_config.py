import logging
import rsa
from config.zoneConfig import  *


log_level = logging.ERROR
async_log_level = logging.ERROR
redis_log_level = logging.WARNING
async_http_log_level = logging.WARNING

redis_config = {

    userConfig:{
        'address':redis_address_list_for_user,

        'hashRing':0,
        'dbIndex':redis_user_data_db,
        'pwd':redis_pwd,
    },

    miscConfig:{
        'address':redis_address_for_misc,

        'hashRing':0,
        'dbIndex':redis_misc_db,
        'pwd':redis_pwd,
    },

    matchConfig:{
        'address':redis_address_for_match,

        'hashRing':0,
        'dbIndex':redis_match_data_db,
        'pwd':redis_pwd,
    },
}



redis_config_debug = {

    userConfig:{
        'address':redis_debug_address_list_for_user,

        'hashRing':0,
        'dbIndex':redis_user_data_db,
        'pwd':redis_pwd,
    },

    miscConfig:{
        'address':redis_debug_address_for_misc,

        'hashRing':0,
        'dbIndex':redis_misc_db,
        'pwd':redis_pwd,
    },
    matchConfig:{
        'address':redis_debug_address_for_match,

        'hashRing':0,
        'dbIndex':redis_match_data_db,
        'pwd':redis_pwd,
    },
}



redis_online_config = {
    onlineConfig:{
        'address':redis_address_for_online,
        'hashRing':0,
        'dbIndex':redis_online_db,
        'pwd':redis_pwd},
}



redis_push_config = {
    pushConfig:{
        'address':redis_address_for_push,
        'hashRing':0,
        'dbIndex':redis_push_db,
        'pwd':redis_pwd},
}



redis_online_config_debug = {
    onlineConfig:{
        'address':redis_debug_address_for_online,
        'hashRing':0,
        'dbIndex':redis_online_db,
        'pwd':redis_pwd},
}


redis_push_config_debug = {
    pushConfig:{
        'address':redis_debug_address_for_push,
        'hashRing':0,
        'dbIndex':redis_push_db,
        'pwd':redis_pwd},
}


mysqlPwd = "baobaobuku"
mysqlPwd_debug = "baobaobuku"
mysqlAddress = "127.0.0.1"
mysqlAddress_debug = "127.0.0.1"



RSA_PRIVATE ="""-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQDMfvDRzR9CxdMcS0UEDUdppW8/8WN2tXKc9UesNip+BpVDC+oA
CojzyovMUNXxIsVq4Eu3mf/+ZZ/7bt8M8zuyYbDDmd+7IeXtkJpD9wFey33Gr0iP
fBrAOqxpPn/nZ8kv0MBl2nlmu6Vxk7/8ERTRgnBFBgEY5ucXFy0hjxo+8QIDAQAB
AoGANLrq1/5/eBVQqXQTOMc/ydMZy7AvyJVjF2v77kENVe/WnzI8RYRx6gMpZybU
89fWdgeeHpq8Mtn7lbbyFwHFO3R10qItsuvMauod2UDMn3wzpE3ke0gC6lgJLljJ
/Yd67a3B9HbVkDGE+N9DLyBNPxvN7vW0o3Z06EeWXp6vEFECQQD8xeWpaCuYyCx9
rRl8S7rnGnW+MBMMy5eH71yUp1H3LesFMYbGo4iGtMicMxWmEVQUB3It7tRi1eR+
sNG1zZiNAkEAzxtEGl0YHCFk7kE0vYxLdLlalV9s5liAG491+oInpjI1j2hcFrp6
fvhKArbXXi1LZNmUc5SDwsM3KcDELQRA9QJBAILR8QByF04lG1GXyr7Xes2slg9u
Vg2jOLNzoBiXWAZzT1UKwtP/QuNkoQamMagXA8qx59f56RWV2YHwBTjwROkCQAlS
iuA87IbnoelvmfYmSIc6iK9MmlRMC4gyDvd1wF8kx3BrHCoRvs3UU1CH9m3Q0CH8
AUiqmLu9mdARU0NLe7kCQBFYlBPrSsWXR9FwGwbi+KuIGrcwGXlZsFh5ptPCkAiA
3sgr27IWSbIRs78GhXH96m7JNLzJ8ax5Ye9d3MYg1mQ=
-----END RSA PRIVATE KEY-----"""


RSA_PUBLIC_PKCS_8="""-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDMfvDRzR9CxdMcS0UEDUdppW8/
8WN2tXKc9UesNip+BpVDC+oACojzyovMUNXxIsVq4Eu3mf/+ZZ/7bt8M8zuyYbDD
md+7IeXtkJpD9wFey33Gr0iPfBrAOqxpPn/nZ8kv0MBl2nlmu6Vxk7/8ERTRgnBF
BgEY5ucXFy0hjxo+8QIDAQAB
-----END PUBLIC KEY-----"""

RSA_PUBLIC_PKCS_1="""-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDMfvDRzR9CxdMcS0UEDUdppW8/
8WN2tXKc9UesNip+BpVDC+oACojzyovMUNXxIsVq4Eu3mf/+ZZ/7bt8M8zuyYbDD
md+7IeXtkJpD9wFey33Gr0iPfBrAOqxpPn/nZ8kv0MBl2nlmu6Vxk7/8ERTRgnBF
BgEY5ucXFy0hjxo+8QIDAQAB
-----END PUBLIC KEY-----"""


g_PubPem = rsa.PublicKey.load_pkcs1_openssl_pem(RSA_PUBLIC_PKCS_8)
g_PriPem = rsa.PrivateKey._load_pkcs1_pem(RSA_PRIVATE)

short_redirect = "http://probet.xyz:8081/urlshortlink/payurlredirect?shorturl={}"

#这个pocoxxx不能改
poco_pay_secret = "39188e5dd4b17537e2f8d8f7c6b32101"

#是否是跳转到代理的页面上
pinboProxyPage = True
pinboProductSitePrefix = "http://zxyxxni.tender88.com"
pinboProductSitePrefixForHttps = "https://zxyxxni.tender88.com"
pinboProxySit = "http://pinnacle.probet.com"
pinboProductSite = "{}/zh-cn/sports/e-sports".format(pinboProductSitePrefix)
