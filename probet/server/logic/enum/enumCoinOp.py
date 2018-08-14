class CoinOp(object):
    coinOpNone = 0
    coinOpPay = 1      #存款
    coinOpDraw = 2     #取款
    coinOpTrans = 3    #转款
    coinOpBet = 4      #押注
    coinOpBetBack = 5  #押注退回
    coinOpAdminOp = 6  #变更金额(扣款）
    coinOpPingboDayWaterRebate = 7   #平博反水
    coinOpProbetDayWaterRebate = 8   #电竞反水
    coinOpActiveAward=9              #活动反奖
    coinOpCommission=10              #返佣
    coinOpRecharge=11                #变更金额(充值）
