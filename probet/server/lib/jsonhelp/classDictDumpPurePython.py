from csprotocol.protoBase import classProtoBase

def class2ProtoDict(check_class):

    if isinstance(check_class,int):
        return check_class
    elif isinstance(check_class,str):
        return check_class
    elif isinstance(check_class,bool):
        return check_class
    elif isinstance(check_class,bytearray):
        return bytes(check_class)
    elif isinstance(check_class,bytes):
        return check_class
    elif isinstance(check_class,float):
        return check_class
    elif isinstance(check_class,list):
        ret = []
        for var_item in check_class:
            ret.append(class2ProtoDict(var_item))
        return ret

    elif isinstance(check_class,dict):
        ret = {}
        for var_key,var_item in check_class.items():
            ret[var_key] = class2ProtoDict(var_item)
        return ret

    elif isinstance(check_class,set):
        ret = []
        for var_item in check_class:
            ret.append(class2ProtoDict(var_item))
        return ret
    else:
        #other type only support baseproto childclass
        if not issubclass(check_class.__class__,classProtoBase):
            #support baseProto childclass
            raise Exception()
        else:
            ret_dict = check_class.__dict__
            for var_dict_key, var_item in ret_dict.items():
                ret_dict[var_dict_key] = class2ProtoDict(var_item)

            return ret_dict

