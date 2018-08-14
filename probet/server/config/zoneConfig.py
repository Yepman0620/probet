gmConfig = "gmConfig"
userConfig = "userConfig"
matchConfig = "matchConfig"
goodsConfig = "goodsConfig"
pushConfig = "pushConfig"
onlineConfig= "onlineConfig"
miscConfig = "miscConfig"


redis_fifo_db = 0           #本机进程间通信
redis_fifo_cross_db = 0     #跨机的进程间通信

redis_user_data_db = 1      #用户数据db
redis_match_data_db = 2     #比赛数据db
redis_gm_db = 3             #gm数据db
redis_push_db = 4           #推送数据db
redis_online_db = 5         #在线用户信息db
redis_misc_db = 6           #全局的一些数据db

redis_port = 6379

redis_address_for_gm = ("127.0.0.1",redis_port)
redis_address_for_push = ("127.0.0.1",redis_port)
redis_address_for_match = ("127.0.0.1",redis_port)
redis_address_for_online = ("127.0.0.1",redis_port)
redis_address_list_for_user = ("127.0.0.1",redis_port)
redis_address_for_misc = ("127.0.0.1",redis_port)
redis_address_for_cross = ("127.0.0.1",redis_port)

########################################################
redis_debug_address_for_gm = ("127.0.0.1",redis_port)
redis_debug_address_for_push = ("127.0.0.1",redis_port)
redis_debug_address_for_match = ("127.0.0.1",redis_port)
redis_debug_address_for_online = ("127.0.0.1",redis_port)
redis_debug_address_list_for_user = ("127.0.0.1",redis_port)
redis_debug_address_for_misc = ("127.0.0.1",redis_port)
redis_debug_address_for_cross = ("127.0.0.1",redis_port)

redis_address_for_local = ("127.0.0.1",redis_port)


redis_pwd = "baobaobuku"

valid_rate_limit = 1.50