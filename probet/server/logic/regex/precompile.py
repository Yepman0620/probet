import re

TelePhoneRegex=re.compile(r'^1[3|4|5|8|7|6|9][0-9]\d{8}$')


ChineseOrEmptyCharRegex=re.compile(r'[\u4e00-\u9fa5]|\s')

EmptyCharRegex = re.compile(r'\s')

NormalCharRegex =re.compile(r'^[A-Za-z][A-Za-z0-9-]+$')

EmailRegex = re.compile(r"[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?")

#非负整数
NotLessZeroInt = re.compile(r"^[1-9]\d*|0$")

#浮点数据
MoreZeroFloat = re.compile(r"^[1-9]\d*\.\d*|0\.\d*[1-9]\d*$")

Password = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,16}$")

TradePassword = re.compile(r"\d{6}")





if __name__ == "__main__":
    strAccountId = "19616335771"

    if TelePhoneRegex.search(strAccountId) is None:
        print("xxxx")