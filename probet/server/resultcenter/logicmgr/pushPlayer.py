import asyncio
from datawrapper.dataBaseMgr import classDataBaseMgr
from lib.onlineMgr import classOnlineMgr
from lib.pushMgr import classPushMgr
from ssprotocol.dataHeaderDefine import classSSHead
from csprotocol.protocol import pushGuessBetChangeResult,pushPlayerCoin
from csprotocol.protoMatch import protoPushBetResultData,protoGuessHistoryItem,protoPushCoinData

@asyncio.coroutine
def pushMsg(objPlayerData,objBetHisData):

    dictOnlineInfo = yield from classOnlineMgr.getInstance().getOnlineClient(objPlayerData.strAccountId)
    if dictOnlineInfo is not None:
        # 没在线，不用推送了
        objPushSSHead = classSSHead()
        objPushSSHead.strAccountId = objPlayerData.strAccountId
        objPushSSHead.strMsgId = pushGuessBetChangeResult
        objPushSSHead.strClientUdid = dictOnlineInfo['connectUid']

        objRsp = protoPushBetResultData()
        objHisItem = protoGuessHistoryItem(objBetHisData)
        objRsp.listGuessBetList.append(objHisItem)

        yield from classPushMgr.getInstance().push(dictOnlineInfo['host'], dictOnlineInfo['groupId'],
                                                   objPushSSHead, objRsp)

        # 推送一下金钱
        objPushSSHead.strMsgId = pushPlayerCoin
        objRsp = protoPushCoinData()
        objRsp.iCoin = "%.2f"%round(objPlayerData.iGuessCoin/100,2)

        yield from classPushMgr.getInstance().push(dictOnlineInfo['host'], dictOnlineInfo['groupId'],
                                                   objPushSSHead, objRsp)

