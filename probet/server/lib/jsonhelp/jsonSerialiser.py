import json
import sys
import logging

global_str_key_dict ={}

def dict_items_key_string_find(var_value,stack_dep):
    stack_dep+=1
    if stack_dep > 5:
        raise Exception("dict_items_key_convert stack_dep is valid")
    obj_inner_str_key_dic={}
    if type(var_value) == dict:
        for var_var_key,var_var_value in var_value.items():
            if type(var_var_key) == str:
                obj_inner_str_key_dic[var_var_key]=""
                inner_obj_inner_str_key_dic = dict_items_key_string_find(var_var_value,stack_dep)
                for inner_key,inner_value in inner_obj_inner_str_key_dic.items():
                    obj_inner_str_key_dic[inner_key] = inner_value
    elif type(var_value) == list:
        for var_var_item in var_value:
            inner_obj_inner_str_key_dic = dict_items_key_string_find(var_var_item,stack_dep)
            for inner_key,inner_value in inner_obj_inner_str_key_dic.items():
                obj_inner_str_key_dic[inner_key] = inner_value
    return obj_inner_str_key_dic

def init_str_key_dic(obj):
    stack_dep = 0

    if type(obj)==dict:
        return obj
    #如果不是dict,是定义的类结构,默认是的,就先这样写吧
    #先把类成员里面的字串包起来
    obj_inner_str_key_dic = dict_items_key_string_find(obj.__dict__,stack_dep)

    global_str_key_dict[obj.__class__.__name__] = obj_inner_str_key_dic

    return obj.__dict__

def convert_to_builtin_types(obj):

    d = {'_c_':obj.__class__.__name__,
         '_m_':obj.__module__,
        }

    d.update(obj.__dict__)
    return d


def items_key_convert(obj,str_key_dic_obj,stack_dep):
    stack_dep+=1
    if stack_dep > 5:
        raise Exception("dict_items_key_convert stack_dep is valid")

    if type(obj) == dict:
        new_dic = {}
        for key, value in obj.items():
            if (key in str_key_dic_obj):
                new_dic[key] = items_key_convert(value,str_key_dic_obj,stack_dep)
            else:
                try:
                    key = int(key)
                    new_dic[key] = items_key_convert(value,str_key_dic_obj,stack_dep)
                except ValueError:
                    new_dic[key] = items_key_convert(value,str_key_dic_obj,stack_dep)
        return new_dic
    elif type(obj) == list:
        new_list = []
        for var_item in obj:
            new_list.append(items_key_convert(var_item,str_key_dic_obj,stack_dep))
        return new_list
    else:
        return obj


def dict_to_object(d):
    if '_c_' in d:
        stack_dep = 0
        class_name = d.pop('_c_')
        module_name = d.pop('_m_')

        #module = __import__(module_name)
        #上面注释的都是先优化的代码替代版本
        obj_inner_str_key_dic = global_str_key_dict.get(class_name,{})

        try:
            module = sys.modules[module_name]
            class_ = getattr(module, class_name)
            inst = class_()
            temp_dict = items_key_convert(d,obj_inner_str_key_dic,stack_dep)
            for var_key,var_value in temp_dict.items():
                try:
                    inst.__dict__[var_key] = var_value
                except Exception as inner_e:
                    logging.error(repr(inner_e))
            return inst
        except Exception as e:
            #print(repr(e))
            logging.exception(e)
            #如果回退版本，或者cacheinstance里面忘记了 预先导入class，都会进到这里来
            return None
        #args = dict( (key.encode('ascii'), value)
        #             for key, value in d.items())
        #inst = class_(**args)
    else:
        return d

#初始化的时候用,优化性能的
def init_dumps(obj, **args):
    return json.dumps(obj,default=init_str_key_dic, **args).encode()

def dumps(obj, **args):
    return json.dumps(obj,default=convert_to_builtin_types, **args).encode()

def loads(data, **args):

    return json.loads(data,object_hook=dict_to_object, **args)



if "__main__" == __name__:

    from logic.data.baseData import baseData
    class T(baseData):
        def __init__(self):
            self.arrayA = []

    t = T()
    t.arrayA.append(1)
    t.arrayA.append(2)


    bytesObj = dumps(t)
    print(bytesObj)
    obj = loads(bytesObj)
    print(obj)