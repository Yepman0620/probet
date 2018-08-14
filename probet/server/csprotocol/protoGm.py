from csprotocol.protoBase import classProtoBase,classProtoRet

#***********************GM相关的***************************
class protoPushPinboRepireData(classProtoBase,classProtoRet):
    def __init__(self):
        super(protoPushPinboRepireData,self).__init__()
        self.end_time = 0      # 结束时间
        self.repairFlag = 0    # 0表示维护结束 1表示正在维护
        self.surplus_time = 0  # 剩余时间
        self.start_time  = 0   # 开始时间



