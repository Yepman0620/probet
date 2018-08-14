from error.errorCode import errorLogic,exceptionLogic,exceptionLogic


class baseData():
    def __init__(self):
        pass

    def __setattr__(self, key, value):
        if key.startswith("i"):
            if not isinstance(value,int) and not isinstance(value,float):
                raise exceptionLogic(errorLogic.data_version_not_valid)
            self.__dict__[key] = value
        elif key.startswith("str"):
            if not isinstance(value,str):
                raise exceptionLogic(errorLogic.data_version_not_valid)
            self.__dict__[key] = value
        elif key.startswith("array"):
            if not isinstance(value,list):
                raise exceptionLogic(errorLogic.data_version_not_valid)
            self.__dict__[key] = value
        elif key.startswith("dict"):
            if not isinstance(value,dict):
                raise exceptionLogic(errorLogic.data_version_not_valid)
            self.__dict__[key] = value
        elif key.startswith("f"):
            if not isinstance(value,float) and not isinstance(value,int):
                raise exceptionLogic(errorLogic.data_version_not_valid)
            self.__dict__[key] = value
        else:
            if key.startswith("__") and key.endswith("__"):
                #return item
                pass
            else:
                raise exceptionLogic(errorLogic.data_version_not_valid)

    def __getattr__(self, item):
        if item.startswith("i"):
            self.__dict__[item] = 0
            return 0
        elif item.startswith("str"):
            self.__dict__[item] = ""
            return ""
        elif item.startswith("array"):
            self.__dict__[item] = []
            return []
        elif item.startswith("dict"):
            self.__dict__[item] = {}
            return {}
        elif item.startswith('f'):
            self.__dict__[item] = 0.00
            return 0.00
        else:
            if item.startswith("__") and item.endswith("__"):
                #return item
                pass
            else:
                raise exceptionLogic(errorLogic.data_version_not_valid)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)


if __name__ == "__main__":


    class baseTese(baseData):
        def __init__(self):
            super(baseTese, self).__init__()

            self.a = 0
            self.b = 0

    try:
        A = baseTese()

        from lib.jsonhelp import jsonSerialiser
        from lib.jsonhelp import classJsonDump
        import pickle

        buf = pickle.dumps(A)
        AA = pickle.loads(buf)

        A.a = 1
    except Exception as e:
        print(repr(e))
