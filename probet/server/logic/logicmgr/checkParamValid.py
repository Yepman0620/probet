import math

def checkIsString(param):
    #print(type(param))
    if isinstance(param,str):
        return True

    return False


def checkIsInt(param):
    #print(type(param))
    if isinstance(param, int):
        return True

    return False

def checkIsFloat(param):
    #print(type(param))
    if math.isnan(param):
        return False

    if math.isinf(param):
        return False

    if isinstance(param, float):
        return True

    return False

def getString(param):
    if checkIsString(param):
        return param
    elif checkIsInt(param):
        return str(param)
    elif checkIsFloat(param):
        return

    return None


def getDictStrOneParam(dictParam,key):

    if isinstance(dictParam,dict):
        return dictParam.get(key,None)
    else:
        return None

def getDictStrParam(dictParam,*key):

    if isinstance(dictParam,dict):
        retList = []
        for var in key:
            retList.append(dictParam.get(var,None))
        return (retList)
    else:
        return None


def checkStringEmpty(param):
    if not isinstance(param,str):
        return True

    if len(param) <= 0:
        return True

    return False