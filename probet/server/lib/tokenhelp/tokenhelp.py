import base64

import aiohttp
from Crypto.Cipher import AES
import hashlib
import time
from lib.timehelp import timeHelp

# # 以下四个是需要的参数
from error.errorCode import exceptionLogic, errorLogic

PINBO_URL="https://paapistg.oreo88.com/b2b"
AGENT_CODE = 'PSZ40'
AGENT_KEY = '08b7cc3e-1a5e-4568-bb1b-61af647b19c8'
SECRET_KEY = 's0972kh4hPWi6Rlo'
INIT_VECTOR = "RandomInitVector"

#AES 加密如果模式 是cbc 等类型需要padding
BS = 16
TOKEN_LAST_GENERAL_TIME = 0
TOKEN_PINBO = ""
#pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
#unpad = lambda s : s[0:-ord(s[-1])]

def pad(s):
    return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

def unpad(s):
    return s[:-ord(s[len(s) - 1:])]


def decrypt_token(token):
    # 解密token
    token=base64.b64decode(token.encode())

    deAes=AES.new(SECRET_KEY,AES.MODE_CBC,INIT_VECTOR)

    decToken=deAes.decrypt(token)

    decToken=unpad(decToken)

    return decToken



def encrypt_AES(tokenPayLoad):
    # AES加密

    enAes=AES.new(SECRET_KEY,AES.MODE_CBC,IV=INIT_VECTOR)

    tokenPayLoad = pad(tokenPayLoad)

    token=enAes.encrypt(tokenPayLoad.encode())

    return base64.b64encode(token).decode()


def gen_token():
    # 生成pinbo需要的token
    # 1、hashToken = md5(agentCode + timestamp + agentKey)
    timestamp = str(int(time.time() * 1000))
    hashToken=hashlib.md5((AGENT_CODE+timestamp+AGENT_KEY).encode())
    hashToken=hashToken.hexdigest()

    # 2、tokenPayLoad = agentCode|timestamp|hashToken
    tokenPayLoad="{}|{}|{}".format(AGENT_CODE,timestamp,hashToken)

    # 3、token = encryptAES(secretKey, tokenPayLoad)
    token=encrypt_AES(tokenPayLoad)

    return token


def gen_headers():
    global TOKEN_LAST_GENERAL_TIME,TOKEN_PINBO
    if (timeHelp.getNow() - TOKEN_LAST_GENERAL_TIME) >= 10*60:
        TOKEN_PINBO=gen_token()
        TOKEN_LAST_GENERAL_TIME = timeHelp.getNow()

    return {'userCode': AGENT_CODE, 'token': TOKEN_PINBO}


def agent_key(agentId):
    """代理生成token的key"""
    agentKey = agentId + 'youisverygood'
    return agentKey


if __name__ == '__main__':
    token=gen_token()
    print(token)
    print(decrypt_token(token))