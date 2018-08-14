import logging
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