import asyncio
import json
import logging
from error.errorCode import exceptionLogic, errorLogic
from datawrapper.sqlBaseMgr import classSqlBaseMgr
from gmweb.utils.getPingboValidWater import getPingboValidWaterByParams
from gmweb.utils.tools import token_required, permission_required
from lib.constants import MSG_PAGE_COUNT
from lib.jsonhelp import classJsonDump
from lib.timehelp.timeHelp import getNow
from logic.logicmgr.checkParamValid import checkIsInt
from gmweb.protocol.gmProtocol import gameType
from gmweb.protocol.gmProtocol import pingboBetType


class cData():
    def __init__(self):
        self.gameName=""
        self.playType=""
        self.totalBet=0             #总投注单数
        self.totalAccount=0         #总投注人数
        self.totalBetCoin=0         #总投注金额
        self.avgBetCoin=0           #注单均值
        self.totalValidCoin=0       #总有效投注额
        self.awardNum=0             #派奖金额
        self.betRate='0.00'         #注单中奖率
        self.userRate='0.00'        #用户中奖率
        self.winCoinRate='0.00'     #赢的钱占注额比重
        self.profitLoss = 0         # 盈亏
        self.profitLossRatio='0.00' # 盈亏比


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []


@token_required
@permission_required('玩法数据查询')
@asyncio.coroutine
def handleHttp(request: dict):
    """玩法数据查询"""
    objRep = cResp()

    game = request.get('game', '')
    startTime = request.get('startTime', 0)
    endTime = request.get('endTime', 0)
    playName=request.get('playName','')
    channel=request.get('channel')
    pn=request.get('pn',1)

    if (not startTime) and (not endTime):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    if (not checkIsInt(startTime)) or (not checkIsInt(endTime)):
        logging.debug(errorLogic.client_param_invalid)
        raise exceptionLogic(errorLogic.client_param_invalid)

    try:
        conn = classSqlBaseMgr.getInstance(instanceName='probet_oss')
        resp_list=[]
        # 没传查全部游戏
        gameNames=[]
        if game=='':
            gameNames.extend(gameType)
            gameNames.append("pingbo")
        else:
            gameNames.append(game)
            #游戏名称
        for gameName in gameNames:
            playTypes=[]
            if playName:
                playTypes.append(playName)
            else:
                if gameName == "pingbo":
                    for playType in pingboBetType.keys():
                        playTypes.append(playType)
                else:
                    #查probet全部玩法
                    sql="select DISTINCT(playType) from dj_betresultbill WHERE dj_betresultbill.GuessName='{}' ".format(gameName)
                    listRest=yield from conn._exeCute(sql)
                    play_types=yield from listRest.fetchall()
                    if len(play_types)==0:
                        continue
                    for playType in play_types:
                        playTypes.append(playType[0])
            for x in playTypes:
                data=cData()
                #游戏名
                data.gameName=gameName
                #玩法名称
                data.playType=x
                if gameName=="pingbo":
                    data.playType=pingboBetType[int(x)]
                    part1_sql = "select count(wagerId),COUNT(DISTINCT(loginId)),SUM(toRisk),SUM(CASE WHEN winLoss>0 THEN winLoss ELSE 0 END) from dj_pingbobetbill WHERE betType={} AND wagerDateFm BETWEEN {} AND {} AND status='SETTLED'".format(
                        x, startTime, endTime)

                    pingboValidWater=yield from getPingboValidWaterByParams(loginIds=None,startTime=startTime,endTime=endTime,betType=x)
                    part3_sql = "select count(wagerId),COUNT(DISTINCT(loginId)) from dj_pingbobetbill WHERE winLoss>0 AND betType={} AND wagerDateFm BETWEEN {} AND {} ".format(
                        x, startTime, endTime)
                    if channel:
                        pingboValidWater =yield from getPingboValidWaterByParams(loginIds=None, startTime=startTime, endTime=endTime,
                                                               agentId=channel,betType=x)
                        part1_sql = part1_sql + " and agentId='{}' ".format(channel)
                        part3_sql = part3_sql + " and agentId='{}' ".format(channel)
                else:
                    part1_sql = "select count(id),COUNT(DISTINCT(accountId)),SUM(betCoinNum),SUM(winCoin) from dj_betresultbill WHERE dj_betresultbill.GuessName='{}' AND dj_betresultbill.playType='{}' AND dj_betresultbill.resultTime BETWEEN {} AND {}".format(
                        gameName, x, startTime, endTime)

                    part2_sql = "select SUM(betCoinNum) from dj_betresultbill WHERE dj_betresultbill.GuessName='{}' AND dj_betresultbill.playType='{}' AND dj_betresultbill.resultTime BETWEEN {} AND {} AND dj_betresultbill.rate>=1.5".format(
                        gameName, x, startTime, endTime)
                    part3_sql = "select count(id),COUNT(DISTINCT(accountId)) from dj_betresultbill WHERE dj_betresultbill.winCoin>0 AND dj_betresultbill.GuessName='{}' AND dj_betresultbill.playType='{}' AND dj_betresultbill.resultTime BETWEEN {} AND {} ".format(
                        gameName, x, startTime, endTime)
                    if channel:
                        part1_sql=part1_sql+" and agentId='{}' ".format(channel)
                        part2_sql=part2_sql+" and agentId='{}' ".format(channel)
                        part3_sql=part3_sql+" and agentId='{}' ".format(channel)

                # 总投注单数,总投注人数，总投注金额，派奖金额
                listRest=yield from conn._exeCute(part1_sql)
                results=yield from listRest.fetchone()
                data.totalBet=results[0]
                data.totalAccount=results[1]
                if gameName=='pingbo':
                    data.totalBetCoin=0 if results[2] is None else results[2]
                    data.awardNum = 0 if results[3] is None else round(results[3],2)
                    #总有效投注额
                    data.totalValidCoin=pingboValidWater
                else:
                    data.totalBetCoin = 0 if results[2] is None else int(results[2]) / 100
                    data.awardNum = 0 if results[3] is None else int(results[3]) / 100
                    # 总有效投注金额
                    listRest = yield from conn._exeCute(part2_sql)
                    ret = yield from listRest.fetchone()
                    data.totalValidCoin = 0 if ret[0] is None else int(ret[0]) / 100

                # 注单均值
                data.avgBetCoin = 0 if data.totalBet == 0 else round(data.totalBetCoin / data.totalBet,2)
                #中奖注单数，中奖人数
                listRest=yield from conn._exeCute(part3_sql)
                winCount=yield from listRest.fetchone()
                #注单中奖率
                data.betRate=0 if data.totalBet==0 else int(winCount[0])/data.totalBet
                #用户中奖率
                data.userRate=0 if data.totalAccount==0 else int(winCount[1])/data.totalAccount
                #中奖额占注额比重
                data.winCoinRate=0 if data.totalBetCoin==0 else data.awardNum/data.totalBetCoin
                #盈亏
                data.profitLoss=round((data.totalBetCoin-data.awardNum),2)
                #盈亏比
                data.profitLossRatio=0 if data.totalBetCoin==0 else data.profitLoss/data.totalBetCoin
                resp_list.append(data)

        objRep.count=len(resp_list)
        objRep.data=resp_list[(pn-1)*MSG_PAGE_COUNT:pn*MSG_PAGE_COUNT:]
        if pn==1:
            fileName = __name__
            nameList = fileName.split('.')
            methodName = nameList.pop()
            # 日志
            dictActionBill = {
                'billType': 'adminActionBill',
                'accountId': request.get('accountId', ''),
                'action': "玩法数据查询",
                'actionTime': getNow(),
                'actionMethod': methodName,
                'actionDetail': "玩法数据查询",
                'actionIp': request.get('srcIp', ''),
            }
            logging.getLogger('bill').info(json.dumps(dictActionBill))
        return classJsonDump.dumps(objRep)
    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.db_error)
