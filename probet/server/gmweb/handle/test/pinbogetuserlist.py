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
        self.userCode = ""
        self.loginId = ""
        self.firstName = ""
        self.lastName = ""
        self.status = ""
        self.availableBalance = ""
        self.outstanding = ""
        self.createdDate = ""
        self.createdBy = ""


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
    testUrl = "https://paapistg.oreo88.com/b2b/list-player/info"

    dictHead = {}
    dictHead["userCode"] = tokenhelp.agentCode
    dictHead["token"] = base64.b64encode(tokenhelp.token).decode()

    dictBody = {}

    try:
        with aiohttp.Timeout(10):             # 为aiohttp设置超时时间
            global client
            client = aiohttp.ClientSession()         # 设置aiohttp客户端对象

            # 这行代码就是用来发送信息的，代替request的，向安博发送请求，并得到响应
            result = yield from client.get(testUrl, data=dictBody, headers=dictHead)
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
        objEle.ele.userCode = dictDataInfo["userCode"]
        objEle.ele.loginId = dictDataInfo["loginId"]
        objEle.ele.firstName = dictDataInfo["firstName"]
        objEle.ele.lastName = dictDataInfo["lastName"]
        objEle.ele.status = dictDataInfo["status"]
        objEle.ele.availableBalance = dictDataInfo["availableBalance"]
        objEle.ele.outstanding = dictDataInfo["outstanding"]
        objEle.ele.createdDate = dictDataInfo["createdDate"]
        objEle.ele.createdBy = dictDataInfo["createdBy"]
        objRsp.data.append(objEle.ele)

    return classJsonDump.dumps(objRsp)










