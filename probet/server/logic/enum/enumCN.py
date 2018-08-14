import enum

class CN(enum.IntEnum):
    〇, 一, 二, 三, 四, 五, 六, 七, 八, 九, 十 = range(11)



if __name__ == '__main__':
    for i in CN:
        print(i,i.value)