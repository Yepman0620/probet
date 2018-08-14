import logging
from config.zoneConfig import *

getMatchDataFromPlatformInterval = 10     #默认60s去取一次 平台比赛数据

getMatchPreDay = 14

dataPlatformDebugBaseUrl = "http://192.157.193.8:10002"
dataPlatformReleaseBaseUrl = "http://192.157.193.8:10002"
dataPlatformReleaseBaseUrlForDebug = "http://192.157.193.8:10002"
debugAppend = "?XDEBUG_SESSION_START=13323"

dataPlatformPostGetMatchData = "/{}/match/get"

datacenter2result_queue_key = "datacenter2result_pubsub_group"
datacenter2notice_queue_key = "datacenter2notice_pubsub_group"


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
