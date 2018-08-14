import asyncio
import logging
from lib.jsonhelp import classJsonDump
from lib.certifytoken import certify_token
import aiohttp
import json
from error.errorCode import exceptionLogic, errorLogic
from lib.tokenhelp import tokenhelp
from datawrapper.dataBaseMgr import classDataBaseMgr
from appweb.appweb_config import pinboProxyPage,pinboProductSite,pinboProductSitePrefix,pinboProductSitePrefixForHttps,pinboProxySit
from lib.certifytoken import certify_token

class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = {}


@asyncio.coroutine
def handleHttp(request: dict):
    """loginV2接口，用户在系统中不存在会创建一个
    """
    objResp = cResp()

    accountId=request.get('accountId',"")
    locale=request.get('locale')
    sport=request.get('sport')
    token=request.get('token')
    hostName=request.get('hostName',"")
    source = request.get('source', 'pc')
    if not source:
        raise exceptionLogic(errorLogic.login_token_not_valid)

    if len(accountId) <= 0:
        objResp.data["loginUrl"] = getPinboProxyUrl(hostName,pinboProductSite)
        return classJsonDump.dumps(objResp)

    certify_token(accountId, token)
    objPlayerData=yield from classDataBaseMgr.getInstance().getPlayerData(accountId)
    if objPlayerData is None:
        raise exceptionLogic(errorLogic.player_data_not_found)

    if source == 'pc':
        if objPlayerData.strToken!=token:
            logging.debug(errorLogic.login_token_not_valid)
            raise exceptionLogic(errorLogic.login_token_not_valid)
    elif source == 'app':
        if objPlayerData.strAppToken!=token:
            logging.debug(errorLogic.login_token_not_valid)
            raise exceptionLogic(errorLogic.login_token_not_valid)

    url="/player/loginV2"
    headers=tokenhelp.gen_headers()

    data={}
    data['loginId']='probet.'+accountId
    data['locale']=locale if locale else 'zh-cn'
    #不用客户端的地址，hardcode
    data['sport']="e-sports"

    try:
         with (aiohttp.ClientSession()) as session:
            with aiohttp.Timeout(10):
                resp=yield from session.post(url=tokenhelp.PINBO_URL+url,data=data,headers=headers,verify_ssl=False)
                if resp.status!=200:
                    logging.error("loginV2 failed [{}]".format(resp.status))
                    raise exceptionLogic(errorLogic.third_party_error)

    except Exception as e:
        logging.exception(e)
        raise exceptionLogic(errorLogic.sys_unknow_error)
    else:

        res = yield from resp.read()
        logging.info(res)
        res = json.loads(res.decode())
        code = res.get('code', '')
        if code != '' and (code in errorLogic.pinbo_error_code.keys()):
            logging.error(code + ":" + errorLogic.pinbo_error_code[code])
            raise exceptionLogic([code, errorLogic.pinbo_error_code[code]])

        objResp.data["loginUrl"] = getPinboProxyUrl(hostName,res["loginUrl"])

        return classJsonDump.dumps(objResp)



def getPinboProxyUrl(hostName,pinboUrl):
    if pinboProxyPage:
        #
        # if len(hostName) > 0:
        #     if hostName.find("192.168") >= 0:
        #         #TODO 这个拿到配置里面
        #         hostName = "www.probet.com"
        #         # cut 4 把 wwww. 前缀去掉
        #     pinboUrl = pinboUrl.replace(pinboProductSitePrefix, "http://pinnacle.{}".format(hostName[4:]))
        #     pinboUrl = pinboUrl.replace(pinboProductSitePrefixForHttps, "http://pinnacle.{}".format(hostName[4:]))
        #     return pinboUrl
        # else:
        #     # TODO 这个拿到配置里面
        #     hostName = "www.probet.com"
        #     pinboUrl = pinboUrl.replace(pinboProductSitePrefix, "http://pinnacle.{}".format(hostName[4:]))
        #     pinboUrl = pinboUrl.replace(pinboProductSitePrefixForHttps, "http://pinnacle.{}".format(hostName[4:]))
        #     return pinboUrl
        pinboUrl = pinboUrl.replace(pinboProductSitePrefix, pinboProxySit)
        pinboUrl = pinboUrl.replace(pinboProductSitePrefixForHttps, pinboProxySit)
        return pinboUrl

    return pinboUrl