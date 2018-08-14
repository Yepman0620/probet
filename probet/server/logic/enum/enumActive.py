

class enumActiveType(object):
    activePayRebate = 1       #用户领单次返利的活动
    activeVipPayRebate = 2    #用户领每月vip返利活动

class enumActiveAwardType(object):
    awardCoin = 0 #奖励类型－钱
    awardWater = 1#奖励类型－流水

class enumActiveState(object):
    stateGet = 0        #获取活动
    stateFinish = 1     #活动完成
    stateAward = 2      #活动奖励
    stateCancel = 3     #活动取消

class enumActiveRefreshType(object):
    activeRefreshNone = 0       #不刷新
    activeRefreshMonty = 1      #月刷新
    activeRefreshWeek = 2      #周刷新
    activeRefreshDay = 3        #日刷新

class enumActiveExpireType(object):
    activeRefreshExpireNone = 0
    activeRefreshExpireDay = 1  # 日过期


class enumActiveStartType(object):
    startRegist = 0 #注册即拿到活动
    startGet = 1    #主动获取活动

