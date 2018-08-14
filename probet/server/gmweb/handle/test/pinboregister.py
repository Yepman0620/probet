import asyncio
from lib.jsonhelp import classJsonDump
from error.errorCode import exceptionLogic, errorLogic
from lib.tokenhelp import tokenhelp
import aiohttp
import json


class cData():
    def __init__(self):
        self.userCode = ""
        self.loginId = ""


class cResp():
    def __init__(self):
        self.ret = ""
        self.retDes = ""
        self.data = ""


@asyncio.coroutine
def handleHttp(dict_param: dict):
    """
    登陆应该传递的参数有用户名相关的信息
    """
    testUrl = "https://paapistg.oreo88.com/b2b/player/create"

    dictHead = {}
    dictHead["userCode"] = tokenhelp.AGENT_CODE
    dictHead["token"] = tokenhelp.gen_token()

    dictBody = {}
    dictBody["agentCode"] = tokenhelp.AGENT_CODE
    dictBody["loginId"] = "probet.test0009"

    try:
        with aiohttp.Timeout(10):             # 为aiohttp设置超时时间
            global client
            client = aiohttp.ClientSession()         # 设置aiohttp客户端对象

            # 这行代码就是用来发送信息的，代替request的，向安博发送请求，并得到响应
            result = yield from client.post(testUrl, data=dictBody, headers=dictHead)
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
    objRsp = cResp()             # 包含ret和retDes这两个是状态码相关的，这个不用我们设置，会自动设置的，另外一个存放的cData的实例对象。
    objRsp.data = cData()        # 这个类对象包含token值，账号，昵称

    objRsp.data.userCode = dictDataInfo["userCode"]       # 用户的账号
    objRsp.data.loginId = dictDataInfo["loginId"]
    return classJsonDump.dumps(objRsp)










