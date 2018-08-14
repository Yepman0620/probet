from csprotocol.protoBase import classProtoBase


class protoPushPlayerCoin(classProtoBase):
    # 推送用户金币
    def __init__(self):
        self.strAccountId = ""
        self.iCoin = 0


class protoPushPlayerCenterCoin(classProtoBase):
    def __init__(self):
        self.strAccountId = ""
        self.iCenterCoin = 0
        self.strCoinKind=""
