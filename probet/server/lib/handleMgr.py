import sys
import os
import re
import importlib
import threading

class HandleImporter():

    _instance = {}
    _instance_lock = threading.Lock()
    _defaultInstance = "default"

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            #if not hasattr(cls, "_instance") or "__instanceName__" in kwargs:
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
            return cls._instance.get(cls._defaultInstance,None)
        else:
            return cls._instance.get(instanceName,None)


    def __init__(self, package, path, file_format, prefixDir):
        self.path = path                      # 这个是请求路径
        self.package = package                # 这个是请求的包
        #self.__dispatch_map = {}
        self.handler_map={}                   # 这个是处理的函数
        self.file_format = file_format        # 这个字面意思是文件形式
        self.prefixDir = prefixDir            # 字面意思是列表前缀


    def load_model(self,filename,routePath):      # 方法名为加载模型

        if os.path.isdir(filename):               # 判断filename是否为路径
            temp_list = os.listdir(filename)      # 如果是路径，则将文件夹下面的所有的文件全部获取出来
            for child_filename in temp_list:      # 遍历这个文件列表
                checkName = filename + child_filename           # 建立完整的名字
                if os.path.isdir(checkName):                    # 如果这个文件依然是文件夹
                    if child_filename != "__pycache__":       # 如果这个子文件名字不为__pycache__
                        self.load_model(checkName + "/","{}/{}".format(routePath,child_filename))    # 使这个实例对象从新调用一次这个函数，只不过目录更加深了一步
                    else:
                        pass
                else:

                    self.load_model(checkName, routePath)       # 这个也是将这个方法再重新调用一回
        else:              # 如果这个直接是文件，那么将查找这个文件
            objGroup = re.search(r'([^\/]+)\.py', filename)
            if objGroup is None:       # 如果匹配不到文件，则说明路径不对
                return

            modname = objGroup.group(1)         # 获取到传入的文件名的不含后缀的部分。
            if modname == '__init__' or modname == '.' or modname == '..':         # 如果为__init__文件，则直接返回即可
                return


            importPath = routePath.replace("/", ".")        # replace的作用是将旧的替换成新的

            try:
                m = importlib.import_module(self.prefixDir + self.package + importPath + '.' + modname)     # 括号内为一个字符串，
                for k in dir(m):
                    # if k.startswith('__') and k.endswith('__'):
                    #    continue
                    if k != "handleHttp":  # 如果k不等于handleHttp，就不用执行
                        continue

                    # cls = getattr(m,k)
                    if (k in self.handler_map):  # 如果k值在处理函数中，则说明复制了原始类
                        raise Exception("duplicated proto class {}".format(k))
                    handleName = routePath + "/" + modname  # 处理的名字的拼接
                    self.handler_map[handleName[1:]] = m.handleHttp  # 可以把handle里面的处理都实例 一个class 来处理，详细参见以前的项目
                    break
            except Exception as e:
                print(repr(e))
                exit(0)



    def load_all(self):        # 加载所有的信息

        try:
            sys.path.append(self.path)         # 将路径添加到系统路径当中去
            #format_arr = self.file_format.split("|")
            path = self.path+'/{}/'.format(self.package)          # 将路径换成新的路径
            self.load_model(path,"")            # 再次调用这个函数

        except Exception as e:
            print(repr(e))
            raise

    def get_handler(self, cmd:str):          # 处理函数
        #return self.__dispatch_map.get(cmd)
        if cmd in self.handler_map:         # 如果cmd在处理函数中，则返回cls，否则返回空
            cls = self.handler_map[cmd]
            return cls
        else:
            return None


