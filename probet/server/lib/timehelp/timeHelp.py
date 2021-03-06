from datetime import datetime
import time


def date2Str(date, format = "%Y-%m-%d %H:%M:%S"):
    return datetime.strftime(date,format)

def str2Date(strDate, format = "%Y-%m-%d %H:%M:%S"):
    return datetime.strptime(strDate,format)

def date2timestamp(date):
    # 时间对象转时间戳
    return int(time.mktime(date.timetuple()))

def strToTimestamp(strDate, format = "%Y-%m-%d %H:%M:%S")->int:
    return int(str2Date(strDate,format).timestamp())

def str2TimeStamp(strDate,format='%Y-%m-%d')->int:
    return int(str2Date(strDate,format).timestamp())

def timestamp2Str(timestamp:int, format = "%Y-%m-%d %H:%M:%S")->str:
    return date2Str(datetime.fromtimestamp(timestamp),format)

def getNow()->int:
    tc = datetime.now().timetuple()
    return int(time.mktime(tc))

def getNowMsec()->int:
    return int(time.time() * 1000)

def isSameDay(timestampA,timestampB):
    a = int((timestampA + 8 * 3600)/ 86400)
    b = int((timestampB + 8 * 3600)/ 86400)

    if a == b:
        return True
    return False

def isSameBetDay(timestampA,timestampB):
    a = int((timestampA + 20 * 3600) / 86400)
    b = int((timestampB + 20 * 3600) / 86400)

    if a == b:
        return True
    return False

def isSameHour(timestampA,timestampB):
    a = int(timestampA / 3600)
    b = int(timestampB / 3600)

    if a == b:
        return True
    return False


# 今天内
def todayStartTimestamp():
    iNow = getNow()
    return iNow - (iNow % 86400)

# 三天内
def threeDayTimestamp():
    iNow = getNow()
    return iNow - (iNow % 86400) - 86400*2

# 七天内
def sevenDayTimestamp():
    iNow = getNow()
    return iNow - (iNow % 86400) - 86400*6

# 三十天内
def thirtyDayTimestamp():
    iNow = getNow()
    return iNow - (iNow % 86400) - 86400*29

def todayEndTimestamp():
    iNow = getNow()
    return iNow + (86400 - iNow % 86400)

def getDate(timestamp:int)->datetime:
    return datetime.fromtimestamp(timestamp)

"""
day in month, 1~31
"""
def getDay(timestamp:int)->int:
    return getDate(timestamp).day

"""
month in year,1~12
"""
def getMonth(timestamp:int)->int:
    return getDate(timestamp).month

"""
year from  1970-01-01, 00:00:00, UTC 0
"""
def getYear(timestamp:int)->int:
    return getDate(timestamp).year

"""
(year, week in year, day in week)
"""
def getWeek(timestamp:int)->(int, int):
    isocalendar = getDate(timestamp).isocalendar()
    return (isocalendar[0], isocalendar[1])

def isSameWeek(timestamp_1, timestamp_2):
    return getWeek(timestamp_1) == getWeek(timestamp_2)

def isSameMonth(timestamp_1, timestamp_2):
    date1 = getDate(timestamp_1)
    date2 = getDate(timestamp_2)
    return date1.month == date2.month


def isSameTimeByDate(timestamp_1, timestamp_2):
    date1 = datetime.fromtimestamp(timestamp_1)

    date2 = datetime.fromtimestamp(timestamp_2)

    if (date1.year == date2.year and
        date1.month == date2.month and
        date1.day == date2.day):
        return True
    else:
        return False


def monthStartTimestamp():
    now = datetime.now()
    begin = datetime(now.year,now.month,1)
    return date2timestamp(begin)

def nextMonthStartTimestamp():
    now = datetime.now()
    begin = datetime(now.year, now.month+1,1)
    return date2timestamp(begin)

def lastMonthStartTimestamp():
    now = datetime.now()
    if now.month <= 1:
        begin = datetime(now.year - 1, 12, 1)
    else:
        begin = datetime(now.year, now.month - 1, 1)
    return date2timestamp(begin)

def getTimeOClockOfToday():
    #获取当天0点时间戳
    t = time.localtime(time.time())
    time1 = time.mktime(time.strptime(time.strftime('%Y-%m-%d 00:00:00', t),'%Y-%m-%d %H:%M:%S'))
    return int(time1)

if __name__ == "__main__":

    #测试账号
    # if isSameTimeByDate(1521388800,1521388799):
    #     print("xxx")
    # print(getTimeOClockOfToday())
    print(timestamp2Str(getNow()))
    # if isSameDay(1521388800,1521388799):
    #     print("yyy")
    #
    # print(getNowMsec())
    #
    # print(monthStartTimestamp())
    # print(lastMonthStartTimestamp())
    # print(nextMonthStartTimestamp())