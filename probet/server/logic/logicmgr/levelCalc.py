from config.vipConfig import vip_config,vipMaxLevel

def calPlayerVipLevel(vipLevel,nowExp,addExp):

    if vipLevel >= vipMaxLevel:
        return vipLevel,nowExp

    dictCurrentLevelCfg = vip_config.get(vipLevel,None)

    nowExp = nowExp + addExp

    while nowExp >= dictCurrentLevelCfg['upGradeValidWater']:
        nowExp = nowExp - dictCurrentLevelCfg['upGradeValidWater']
        if vipLevel + 1 >= vipMaxLevel:
            vipLevel = vipMaxLevel
            nowExp = 0
            return vipLevel,nowExp

        vipLevel += 1

        dictCurrentLevelCfg = vip_config.get(vipLevel, None)


    return vipLevel,nowExp