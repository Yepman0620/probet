import asyncio
from lib.jsonhelp import classJsonDump
from error.errorCode import exceptionLogic, errorLogic
from lib.tokenhelp import tokenhelp
import aiohttp
import json
import base64

class cElement():
    def __init__(self):
        self.ele = ""


class cData():
    def __init__(self):
        self.wagerId = ""
        self.eventName = ""
        self.parentEventName = ""
        self.headToHead = ""
        self.wagerDateFm = ""
        self.eventDateFm = ""
        self.settleDateFm = ""
        self.status = ""
        self.homeTeam = ""
        self.awayTeam = ""
        self.selection = ""
        self.handicap = ""
        self.odds = ""
        self.oddsFormat = ""
        self.betType = ""
        self.league = ""
        self.stake = ""
        self.sport = ""
        self.currencyCode = ""
        self.inplayScore = ""
        self.inPlay = ""
        self.homePitcher = ""
        self.awayPitcher = ""
        self.homePitcherName = ""
        self.awayPitcherName = ""
        self.period = ""
        self.cancellationStatus = ""
        self.parlaySelections = ""
        self.category = ""
        self.toWin = ""
        self.toRisk = ""
        self.product = ""
        self.parlayMixOdds = ""
        self.competitors = ""
        self.userCode = ""
        self.loginId = ""
        self.winLoss = ""
        self.turnover = ""
        self.scores = ""
        self.result = ""

class cResp():
    def __init__(self):
        self.ret = ""
        self.retDes = ""
        self.data = []


@asyncio.coroutine
def handleHttp(dict_param: dict):
    """
    登陆应该传递的参数有用户名相关的信息
    """
    testUrl = "https://paapistg.oreo88.com/b2b/report/wagers?dateFrom=2018-05-11 17:25:00&dateTo=2018-05-12 17:25:00&product=SB&userCode=PSZ4000002"

    dictHead = {}
    dictHead["userCode"] = tokenhelp.agentCode
    dictHead["token"] = base64.b64encode(tokenhelp.token).decode()
    print(dictHead['token'])

    try:
        with aiohttp.Timeout(10):             # 为aiohttp设置超时时间
            global client
            client = aiohttp.ClientSession()         # 设置aiohttp客户端对象

            # 这行代码就是用来发送信息的，代替request的，向安博发送请求，并得到响应
            result = yield from client.get(testUrl, headers=dictHead)
            if result.status != 200:            # 发送请求失败
                print('get status failed [{}]'.format(result.status))
                raise exceptionLogic(errorLogic.client_param_invalid)
            else:            # 等到请求之后，再去读取返回来的信息
                ret = yield from result.read()
                ret = ret.decode('utf-8')
                print(ret)
                global dictDataInfo
                dictDataInfo = json.loads(ret)
                print(dictDataInfo)
    except Exception as e:
        raise exceptionLogic(errorLogic.sys_unknow_error)
    finally:
        if client is not None:
            yield from client.close()
    #构造回包
    objRsp = cResp()
    objEle = cElement()
    objEle.ele = cData()

    for dictDataInfo in dictDataInfo:
        objEle.ele.wagerId = dictDataInfo["wagerId"]
        objEle.ele.eventName = dictDataInfo["eventName"]
        objEle.ele.parentEventName = dictDataInfo["parentEventName"]
        objEle.ele.headToHead = dictDataInfo["headToHead"]
        objEle.ele.wagerDateFm = dictDataInfo["wagerDateFm"]
        objEle.ele.eventDateFm = dictDataInfo["eventDateFm"]
        objEle.ele.settleDateFm = dictDataInfo["settleDateFm"]
        objEle.ele.status = dictDataInfo["status"]
        objEle.ele.homeTeam = dictDataInfo["homeTeam"]
        objEle.ele.awayTeam = dictDataInfo["awayTeam"]
        objEle.ele.selection = dictDataInfo["selection"]
        objEle.ele.handicap = dictDataInfo["handicap"]
        objEle.ele.odds = dictDataInfo["odds"]
        objEle.ele.oddsFormat = dictDataInfo["oddsFormat"]
        objEle.ele.betType = dictDataInfo["betType"]
        objEle.ele.league = dictDataInfo["league"]
        objEle.ele.stake = dictDataInfo["stake"]
        objEle.ele.sport = dictDataInfo["sport"]
        objEle.ele.currencyCode = dictDataInfo["currencyCode"]
        objEle.ele.inplayScore = dictDataInfo["inplayScore"]
        objEle.ele.inPlay = dictDataInfo["inPlay"]
        objEle.ele.homePitcher = dictDataInfo["homePitcher"]
        objEle.ele.awayPitcher = dictDataInfo["awayPitcher"]
        objEle.ele.homePitcherName = dictDataInfo["homePitcherName"]
        objEle.ele.awayPitcherName = dictDataInfo["awayPitcherName"]
        objEle.ele.period = dictDataInfo["period"]
        objEle.ele.cancellationStatus = dictDataInfo["cancellationStatus"]
        objEle.ele.parlaySelections = dictDataInfo["parlaySelections"]
        objEle.ele.category = dictDataInfo["category"]
        objEle.ele.toWin = dictDataInfo["toWin"]
        objEle.ele.toRisk = dictDataInfo["toRisk"]
        objEle.ele.product = dictDataInfo["product"]
        objEle.ele.parlayMixOdds = dictDataInfo["parlayMixOdds"]
        objEle.ele.competitors = dictDataInfo["competitors"]
        objEle.ele.loginId = dictDataInfo["loginId"]
        objEle.ele.winLoss = dictDataInfo["winLoss"]
        objEle.ele.turnover = dictDataInfo["turnover"]
        objEle.ele.scores = dictDataInfo["scores"]
        objEle.ele.result = dictDataInfo["result"]
        objRsp.data.append(objEle.ele)


    return classJsonDump.dumps(objRsp)










