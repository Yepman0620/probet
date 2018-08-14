import threading
import asyncio


class classObserver():
    def __init__(self,eventName):
        self.strEventName = eventName

    @asyncio.coroutine
    def update(self,*args,**kwargs):
        pass

    def getEventName(self):
        return self.strEventName


class classSubject():
    _instance = {}
    _instance_lock = threading.Lock()
    _defaultInstance = "default"

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            # if not hasattr(cls, "_instance") or "__instanceName__" in kwargs:
            if "__instanceName__" in kwargs:
                objInstance = cls.getInstance(kwargs["__instanceName__"])
            else:
                objInstance = cls.getInstance(cls._defaultInstance)

            if objInstance is None:
                objNew = object.__new__(cls)
                objNew.__init__(*args, **kwargs)
                # 拥有多个单例对象
                if "__instanceName__" in kwargs:
                    cls._instance[kwargs["__instanceName__"]] = objNew
                else:
                    cls._instance[cls._defaultInstance] = objNew

        return cls._instance

    @classmethod
    def getInstance(cls, instanceName=None):
        if instanceName is None:
            return cls._instance.get(cls._defaultInstance, None)
        else:
            return cls._instance.get(instanceName, None)

    def __init__(self):
        self.dictObserver = {}

    def attach(self,objObserver):
        tempListObs = self.dictObserver.get(objObserver.getEventName(),None)
        if tempListObs is None:
            self.dictObserver[objObserver.getEventName()] = [objObserver]
        else:
            tempListObs.append(objObserver)

    def detach(self,objObserver):
        tempListObs = self.dictObserver.get(objObserver.getEventName(),[])
        if objObserver in tempListObs:
            tempListObs.remove(objObserver)

    @asyncio.coroutine
    def notify(self,eventName,*args,**kwargs):
        tempListObs = self.dictObserver.get(eventName, [])
        for var_fun in tempListObs:
            #TODO 优化成 xiecheng 批量处理
            yield from var_fun.update(args,**kwargs)
