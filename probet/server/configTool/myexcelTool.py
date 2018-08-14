import os

if __name__ == "__main__":

    convertAllExcelFile = open("./allexcel.txt","r")

    for line in convertAllExcelFile.readlines():  # 依次读取每行
        line = line.strip()
        if line[0] == "#" or (line[0] == "/" and line[1] == "/"):
            continue


        ret = os.system("python3.6 myexcel2json.py {} {}".format(line,"../config/"))

        ret = ret >> 0
        if ret != 0:
            print("myexcel2json {} failed".format(line))
