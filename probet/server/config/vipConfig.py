vip_config = {
    0:{
        "level":0,
        "upGradeValidWater":1000000,
        "keepValidWater":0,
        "rebate":4,
        "need_exp": 388,
        "total_exp": 88,
    },
    1:{
        "level":1,
        "upGradeValidWater":50000000,
        "keepValidWater":8000000,
        "rebate":4,
    },
    2:{
        "level":2,
        "upGradeValidWater":200000000,
        "keepValidWater":40000000,
        "rebate":5,
    },
    3:{
        "level":3,
        "upGradeValidWater":500000000,
        "keepValidWater":160000000,
        "rebate":6,
    },
    4:{
        "level":4,
        "upGradeValidWater":9999999999999999999,
        "keepValidWater":400000000,
        "rebate":8,
    },
}

vipMaxLevel = 0

for var_value in vip_config.values():
    if var_value['level'] > vipMaxLevel:
        vipMaxLevel = var_value['level']



