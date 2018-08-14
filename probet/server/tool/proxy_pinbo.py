import sys
from optparse import  OptionParser
import asyncio
import uvloop
import aiohttp
import aiofiles
from aiohttp import web
from multidict import CIMultiDict

g_obj_loop = asyncio.get_event_loop()
g_str_dns = ""
g_root_path = "/var/www/probet" #注意后面没有/
g_proxy_site = "http://zxyxxni.tender88.com"
g_proxy_site_no_prefix_http = "zxyxxni.tender88.com"
#g_proxy_site = "https://www.pronhub.com"

@asyncio.coroutine
def hookStaticFileFunction(request,header):
    objRespHead = CIMultiDict()

    for var_key,var_value in header.items():
        objRespHead.add(var_key,var_value)

    strRealFilePath = g_root_path + request.path
    objFileHandle = yield from aiofiles.open(strRealFilePath, "rb")
    try:
        content = yield from objFileHandle.read()
    finally:
        yield from objFileHandle.close()

    return objRespHead,content

@asyncio.coroutine
def hookReturnFrameLocationFunction(content):
    return b"parent.location.reload();"


g_hook_url = {}
# g_hook_url = {"/member/img/skin6/bg.jpg":{"func":hookStaticFileFunction,"header":{"Content-Type":"image/jpeg;charset=UTF-8"}},
#               "/member/bundles/page.sports.css":{"func":hookStaticFileFunction,"header":{"Content-Type":"text/css;charset=UTF-8"}},
#               "/member/bundles/framework.css":{"func":hookStaticFileFunction,"header":{"Content-Type":"text/css;charset=UTF-8"}},
#               "/member/img/ps3838/odds-change.gif":{"func":hookStaticFileFunction,"header":{"Content-Type":"image/gif;charset=UTF-8"}}
#               }

resultJumpMD5Content = b"window.location.reload(true);"

g_hook_result = {}
# g_hook_result = {"_Incapsula_Resource":{"content":resultJumpMD5Content,"func":hookReturnFrameLocationFunction}
#               }


@asyncio.coroutine
def handlerWebApp(request):
    objResp = web.Response()
    objRespHead = CIMultiDict()
    proxyHeader = {}
    proxyCookie = {}

    for var_head,var_value in request.headers.items():
        if var_head == "Host":
            proxyHeader[var_head] = g_proxy_site_no_prefix_http
        elif var_head == "Origin":
            proxyHeader[var_head] = var_value.replace(g_str_dns, g_proxy_site_no_prefix_http)
        elif var_head == "Referer":
            proxyHeader[var_head] = var_value.replace(g_str_dns, g_proxy_site_no_prefix_http)
            # proxyHeader[var_head[0]] = var_head[1].replace("127.0.0.1:8888", "zxyxxni.tender88.com")
        elif var_head == "Upgrade-Insecure-Requests":
            proxyHeader[var_head] = var_value
        else:
            proxyHeader[var_head] = var_value

    listCookie = request.headers.get('cookie', None)
    if listCookie is not None:
        listCookie = listCookie.split(";")
        for var_cookie in listCookie:
            key = var_cookie.split('=')[0].strip()
            value = var_cookie.split('=')[1].strip()


            tempDns = g_str_dns[g_str_dns.find('.'):]
            tempIndex = tempDns.find(":")
            if tempIndex >= 0:
                tempDns = tempDns[:tempIndex]

            value = value.replace("Domain={}".format(tempDns), "Domain=.tender88.com")
            proxyCookie[key] = value

    print(proxyCookie)
    print("############### cookie end ###############")
    print(proxyHeader)
    print("################ header end #####################")
    ret = yield from request.read()

    #beginTime = time.time()
    print("################ request begin ###############")

    bBlockError = False
    if request.path not in g_hook_url:
        body = b''
        if request.method == "GET":
            print("#######get url [{}]".format(request.raw_path))
            if request.raw_path.find("SWJIYLWA="):
                #这个是跨域报错的返回:
                bBlockError = True

            with aiohttp.ClientSession(cookies=proxyCookie) as session:
                if len(ret) <= 0:
                    resp = yield from session.get(g_proxy_site + request.raw_path, headers=proxyHeader,
                                                  verify_ssl=False)
                else:
                    resp = yield from session.get(g_proxy_site + request.raw_path,data=ret,headers=proxyHeader,verify_ssl=False)
                #print("################ read begin ###############")
                body = yield from resp.read()
                #
                # if bBlockError:
                #     if body.startswith(b'(function() { var z="";var'):
                #         body = b''
                #print("################ read end ###############")
        else:
            print("#########post url [{}]".format(request.raw_path))
            with aiohttp.ClientSession(cookies=proxyCookie) as session:
                resp = yield from session.post(g_proxy_site + request.raw_path,data=ret,headers=proxyHeader,verify_ssl=False)
                #print("################ read begin ###############")
                body = yield from resp.read()
                #print("################ read end ###############")

        objResp._status = resp.status
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print(resp.status)

        for head_key, head_value in resp.headers.items():
            if head_key == "Content-Encoding":
                continue
            elif head_key == "Content-Length":
                continue
            elif head_key == "Transfer-Encoding":
                continue
            elif head_key == "Set-Cookie":
                #print("收到返回的cookie")
                #print(head_value)

                tempDns = g_str_dns[g_str_dns.find('.'):]
                tempIndex = tempDns.find(":")
                if tempIndex >= 0:
                    tempDns = tempDns[:tempIndex]

                objRespHead.add(head_key, head_value.replace("Domain=.tender88.com",
                                                             "Domain={}".format(tempDns)))
            else:
                objRespHead.add(head_key, head_value)

        if request.path in g_hook_result:
            if (g_hook_result[request.path]["content"]) == body:
                body = g_hook_result[request.path]["func"](body)

        objResp.body = body

    else:
        objResp._status = 200
        objHead,objResp.body = yield from g_hook_url[request.path]["func"](request,g_hook_url[request.path]["header"])
        objRespHead.extend(objHead)


    #print("################ request end ###############")
    #print(time.time() - beginTime)
    objRespHead.add("Access-Control-Allow-Origin","*")
    objResp.headers.extend(objRespHead)

    print("####### return code[{}] head[{}] #######".format(200, objRespHead))
    return objResp


@asyncio.coroutine
def __initAppWebServer():
    server = web.Server(handlerWebApp)
    yield from g_obj_loop.create_server(server, "127.0.0.1", 8888)

@asyncio.coroutine
def init():

    g_obj_loop.set_debug(False)
    print("aioevent is {} modle".format(g_obj_loop.get_debug()))
    yield from __initAppWebServer()


if __name__ == "__main__":

    if sys.version_info[0] < 3:
        print("Found Python interpreter less 3.0 version not support: %s \n"%sys.version)
        sys.exit()
    else:
        parser = OptionParser(usage="%prog --rf <runFlag> ", version="%prog 0.3")
        parser.add_option("--rf", "--runFlag", dest="runFlag", help="runFlag debug or release")
        parser.add_option("--dns", "--dns", dest="dns", help="dns")


        (options, args) = parser.parse_args()

        runFlag = str(options.runFlag)
        g_str_dns = str(options.dns)

        if runFlag == "debug":
            pass
        else:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            g_obj_loop = asyncio.get_event_loop()
            pass

        try:
            asyncio.async(init())
            g_obj_loop.run_forever()
        except KeyboardInterrupt as e:
            print(asyncio.Task.all_tasks())
            print(asyncio.gather(*asyncio.Task.all_tasks()).cancel())
            g_obj_loop.stop()
            g_obj_loop.run_forever()
        except:
            # logging.error(traceback.format_exc())
            exit(0)
        finally:
            g_obj_loop.close()