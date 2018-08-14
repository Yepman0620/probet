
commission_config = {
    1:{
        "mostNetWin":50000.00,
        "leastNetWin":0,
        "level":"一档",
    },
    2:{
        "mostNetWin":200000.00,
        "leastNetWin":50000.00,
        "level":"二档",
    },
    3:{
        "mostNetWin":500000.00,
        "leastNetWin":200000.00,
        "level":"三档",
    },
    4:{
        "mostNetWin":800000.00,
        "leastNetWin":500000.00,
        "level":"四档",
    },
    5:{
        "mostNetWin":9999999999999999999,
        "leastNetWin":800000.00,
        "level":"五档",
    },
}



# a = 80000001

# from datawrapper.sqlBaseMgr import classSqlBaseMgr
# agentConfig = yield from getAgentConfig()
# for var_value in commission_config.values():
#     if var_value['leastNetWin'] < a <= var_value['mostNetWin']:
#         level = var_value['level']
#         proportion = agentConfig[level]



