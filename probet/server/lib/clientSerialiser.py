import json
import msgpack

def dumps(debugFlag:bool,obj, **args):
    # 调试的时候用json
    if debugFlag:
        return json.dumps(obj, **args)
    else:
        return msgpack.dumps(obj, **args)

def loads(debugFlag:bool,obj, **args):
    #调试的时候用json
    if debugFlag:
        return json.loads(obj, **args)
    else:
        return msgpack.loads(obj,encoding='utf-8', **args)