import logging
from config.zoneConfig import *



redis_config = {
    matchConfig:{
        'address':redis_address_for_match,

        'hashRing':0,
        'dbIndex':redis_match_data_db,
        'pwd':redis_pwd,
    },
    miscConfig:{
        'address':redis_address_for_misc,
        'hashRing':0,
        'dbIndex':redis_misc_db,
        'pwd':redis_pwd,
    },
    userConfig:{
        'address':redis_address_list_for_user,
        'hashRing':0,
        'dbIndex':redis_user_data_db,
        'pwd':redis_pwd,

    },
    gmConfig:{
        'address':redis_address_for_gm,
        'port':redis_port,
        'hashRing':0,
        'dbIndex':redis_gm_db,
        'pwd':redis_pwd
    },
}



redis_config_debug = {

    matchConfig:{
        'address':redis_debug_address_for_match,

        'hashRing':0,
        'dbIndex':redis_match_data_db,
        'pwd':redis_pwd,
    },
    miscConfig:{
        'address':redis_debug_address_for_misc,
        'hashRing':0,
        'dbIndex':redis_misc_db,
        'pwd':redis_pwd,
    },
    userConfig:{
        'address':redis_debug_address_list_for_user,
        'hashRing':0,
        'dbIndex':redis_user_data_db,
        'pwd':redis_pwd,

    },
    gmConfig:{
        'address':redis_debug_address_for_gm,
        'port':redis_port,
        'hashRing':0,
        'dbIndex':redis_gm_db,
        'pwd': redis_pwd
    },
}


mysqlPwd = "baobaobuku"
mysqlPwd_debug = "baobaobuku"
mysqlAddress = "127.0.0.1"
mysqlAddress_debug = "127.0.0.1"


log_level = logging.WARNING
async_log_level = logging.WARNING
redis_log_level = logging.WARNING