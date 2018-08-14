
class classProtoBase():
    pass

class classProtoRet():
    def __init__(self):
        self.ret = 0
        self.retDes = ""

# 连接成功
class protoConnectReq(classProtoBase):
    def __init__(self):
        pass


class protoConnectResp(classProtoBase):
    def __init__(self):
        self.ret = 0
        self.retDes = ""