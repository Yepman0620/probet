import logging
from config.zoneConfig import *

connect2logic_queue_key = "connect2logic_group[{}]"
logic2connect_queue_key = "logic2connect_group[{}]"

logic2connect_push_queue_key = "logic2connect_push_group[{}]"

all2connect_broadcast_queue_key = "all2connect_broadcast"


log_level = logging.NOTSET
async_log_level = logging.WARNING
redis_log_level = logging.WARNING
websocket_log_level = logging.NOTSET



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
