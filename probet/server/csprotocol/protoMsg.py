from csprotocol.protoBase import classProtoBase,classProtoRet

#***********************消息推送***************************
class protoPushPlayerMsg(classProtoBase,classProtoRet):
    def __init__(self):
        super(protoPushPlayerMsg,self).__init__()
        self.accountId = ""  # 用户名
        self.msgId = ""      # 消息id

