import logging
from config.zoneConfig import *

batch_get_task_num = 10
batch_get_task_time = 60 * 60

gm2result_queue_key = "gm2result_pubsub_group"

log_level = logging.NOTSET
async_log_level = logging.WARNING
redis_log_level = logging.WARNING



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
    pushConfig:{
        'address':redis_address_for_push,
        'hashRing':0,
        'dbIndex':redis_push_db,
        'pwd':redis_pwd,
    },
    onlineConfig:{
        'address':redis_address_for_online,
        'hashRing':0,
        'dbIndex':redis_online_db,
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
    matchConfig:{
        'address':redis_debug_address_for_match,
        'hashRing':0,
        'dbIndex':redis_match_data_db,
        'pwd':redis_pwd,
    },
    pushConfig:{
        'address':redis_debug_address_for_push,

        'hashRing':0,
        'dbIndex':redis_push_db,
        'pwd':redis_pwd,
    },
    onlineConfig:{
        'address':redis_debug_address_for_online,
        'hashRing':0,
        'dbIndex':redis_online_db,
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
