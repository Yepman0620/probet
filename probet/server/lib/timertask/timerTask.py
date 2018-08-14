#import bisect
import uuid
from lib.timehelp import timeHelp

class classTask:
    def __init__(self):
        self.uid = ''
        self.account_id = ''
        self.userDefineID = ''
        self.userDefineFinshTime = 0
        self.call_back_fun = None

class classTaskTimer:
    def __init__(self):
        self.task_array = []


    def loadData(self,task_array):
        pass

    def create_task(self,account_id,userDefineID,userDefineFinshTime,call_back_fun):
        temp_task = classTask()
        temp_task.uid = uuid.uuid1()
        temp_task.account_id = account_id
        temp_task.userDefineFinshTime = userDefineFinshTime
        temp_task.userDefineID = userDefineID
        temp_task.call_back_fun = call_back_fun

        return temp_task

    def create_task_and_insert(self,account_id,userDefineID,userDefineFinshTime,call_back_fun):

        new_task = self.create_task(account_id,userDefineID,userDefineFinshTime,call_back_fun)

        self.bin_insert_right_sort(new_task)

    def load_task(self):
        pass

    def loop_logic(self):
        finish_num = 0
        for var in self.task_array:
            if var.userDefineFinshTime >= timeHelp.getNow():
                #时间到了,触发逻辑
                if var.call_back_fun != None:
                    var.call_back_fun(var.account_id,var.userDefineID)

                finish_num+=1
            else:
                break

        #因为是按时间有序的,就按头部弹出就可以了
        while finish_num > 0:
            finish_num-=1
            self.task_array.pop(0)

    #排序
    def insert_sort(self):
        for i in range(len(self.task_array)):
            min_index = i
            for j in range(i+1,len(self.task_array)):
                if self.task_array[min_index].userDefineFinshTime > self.task_array[j].userDefineFinshTime:
                    min_index = j
            tmp = self.task_array[i]
            self.task_array[i] = self.task_array[min_index]
            self.task_array[min_index] = tmp

    #bin插入排序,插入右边
    def bin_insert_right_sort(self,insert_task:classTask,lo=0,hi=None):
        if lo < 0:
            raise ValueError('lo must be non-negative')
        if hi is None:
            hi = len(self.task_array)
        while lo < hi:
            mid = (lo+hi)//2
            if insert_task.userDefineFinshTime < self.task_array[mid].userDefineFinshTime: hi = mid
            else: lo = mid+1
        self.task_array.insert(lo, insert_task)
        return lo

'''
array_test=[0,1,4,6,5,6,7,1,8]

sort_array=[]
for var in array_test:
    bisect.insort(sort_array,var)

array_test.insert(0,9)
print(array_test)

print(sort_array)
'''
