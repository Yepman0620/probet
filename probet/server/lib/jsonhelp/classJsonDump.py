import json
from csprotocol.protoBase import classProtoBase


'''
try:
    import logging
    if not log.checkInitFlag():
        raise exceptionLogInit("log shoud import at begin python first line")
except exceptionLogInit:
    try:
        from lib.multiprocesslogbysyshandler import multiPLogger as log
        if not log.checkInitFlag():
            raise exceptionLogInit("log shoud import at begin python first line")
    except Exception as e:
        raise e

except Exception as e:
    raise e
'''


def convert_to_builtin_types(obj):
    '''
    if isinstance(obj,int):
        return obj
    elif isinstance(obj,str):
        return obj
    elif isinstance(obj,bool):
        return obj
    elif isinstance(obj,dict):
        return obj
    elif isinstance(obj,bytearray):
        return bytes(obj)
    elif isinstance(obj,bytes):
        return obj
    elif isinstance(obj,float):
        return obj
    else:
        #other type only support baseproto childclass
        if not issubclass(obj.__class__,classProtoBase):
            #support baseProto childclass
            raise Exception()
        else:
            return obj.__dict__
    '''
    # print(type(obj))
    return obj.__dict__

def dumps(obj, **args):
    return json.dumps(obj,default=convert_to_builtin_types, **args).encode()

if __name__ == '__main__':
    print(convert_to_builtin_types(classProtoBase))