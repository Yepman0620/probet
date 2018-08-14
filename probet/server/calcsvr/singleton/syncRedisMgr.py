import redis as synchronous_redis_lib
from config import zoneConfig

g_obj_synchronous_redis = synchronous_redis_lib.StrictRedis(host=zoneConfig.redis_address_for_misc[0],
                                    port=zoneConfig.redis_address_for_misc[1],
                                    db=zoneConfig.redis_misc_db, socket_timeout=10, password=zoneConfig.redis_pwd)