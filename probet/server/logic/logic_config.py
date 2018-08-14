import logging
from config.zoneConfig import  *

connect2logic_queue_key = "connect2logic_group[{}]"
logic2connect_queue_key = "logic2connect_group[{}]"

logic2connect_push_queue_key = "logic2connect_push_group[{}]"

all2connect_broadcast_queue_key = "all2connect_broadcast"



log_level = logging.NOTSET
async_log_level = logging.WARNING
redis_log_level = logging.WARNING

redis_gm_config = {
    gmConfig:{
        'address':redis_address_for_gm,

        'hashRing':0,
        'dbIndex':redis_gm_db,
        'pwd':redis_pwd},
}


redis_gm_config_debug = {
    gmConfig:{
        'address':redis_debug_address_for_gm,

        'hashRing':0,
        'dbIndex':redis_gm_db,
        'pwd': redis_pwd},
}



redis_config = {

    userConfig:{
        'address':redis_address_list_for_user,

        'hashRing':0,
        'dbIndex':redis_user_data_db,
        'pwd':redis_pwd,
    },
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

    pushConfig:{
        'address':redis_address_for_push,

        'hashRing':0,
        'dbIndex':redis_push_db,
        'pwd':redis_pwd,
    },


    gmConfig:{
        'address':redis_address_for_gm,

        'hashRing':0,
        'dbIndex':redis_gm_db,
        'pwd':redis_pwd
    },


}



redis_config_debug = {

    userConfig:{
        'address':redis_debug_address_list_for_user,

        'hashRing':0,
        'dbIndex':redis_user_data_db,
        'pwd':redis_pwd,
    },
    matchConfig:{
        'address':redis_debug_address_for_match,

        'hashRing':0,
        'dbIndex':redis_match_data_db,
        'pwd':redis_pwd,
    },

    miscConfig: {
        'address': redis_debug_address_for_misc,
        'hashRing': 0,
        'dbIndex': redis_misc_db,
        'pwd': redis_pwd,
    },
    pushConfig:{
        'address':redis_debug_address_for_push,
        'hashRing':0,
        'dbIndex':redis_push_db,
        'pwd':redis_pwd,
    },


    gmConfig:{
        'address':redis_debug_address_for_gm,
        'hashRing':0,
        'dbIndex':redis_gm_db,
        'pwd': redis_pwd
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
