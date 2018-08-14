import asyncio
from lib.jsonhelp import classJsonDump
from datawrapper.dataBaseMgr import classDataBaseMgr
import random

last_names = ['赵', '钱', '孙', '李', '周', '吴', '郑', '王', '冯', '陈', '褚', '卫', '蒋', '沈', '韩', '杨', '朱', '秦', '尤', '许',
              '姚', '邵', '堪', '汪', '祁', '毛', '禹', '狄', '米', '贝', '明', '臧', '计', '伏', '成', '戴', '谈', '宋', '茅', '庞',
              '熊', '纪', '舒', '屈', '项', '祝', '董', '梁']

first_names = ['的', '一', '是', '了', '我', '不', '人', '在', '他', '有', '这', '个', '上', '们', '来', '到', '时', '大', '地', '为',
               '子', '中', '你', '说', '生', '国', '年', '着', '就', '那', '和', '要', '她', '出', '也', '得', '里', '后', '自', '以',
               '乾', '坤', '']

head_urls = ["http://img2.100bt.com/upload/ttq/20130303/1362279957772.jpg",
             "http://www.qqzhuangban.com/uploadfile/2014/06/1/20140619090721688.jpg",
             "http://img1.imgtn.bdimg.com/it/u=3007568175,3259995008&fm=27&gp=0.jpg",
             "http://www.qqkubao.com/uploadfile/2014/10/1/20141011185233670.jpg",
             "http://a3.gexing.com/G1/M00/87/91/rBACE1TwL0-T4oCWAACyLtQjeJk470200.jpg",
             "http://www.ld12.com/upimg358/allimg/20160713/zbgp0htvky567.jpg",
             "http://a.hiphotos.baidu.com/zhidao/wh%3D450%2C600/sign=43a3317616ce36d3a2518b340fc316b1/2f738bd4b31c8701b99d7f4a247f9e2f0708ff77.jpg",
             "http://www.qqzhuangban.com/uploadfile/2014/07/1/20140720035650616.jpg",
             "http://c.hiphotos.baidu.com/zhidao/wh%3D450%2C600/sign=94fbc0482b381f309e4c85ad9c31603e/a5c27d1ed21b0ef411016a2edec451da80cb3ed0.jpg",
             "http://pic2.52pk.com/files/150130/4444414_100350_5671.png",
             "http://www.qqzhuangban.com/uploadfile/2014/08/1/20140802065634399.jpg",
             "http://img5.duitang.com/uploads/item/201410/01/20141001142703_4JVXv.jpeg",
             "http://img1.touxiang.cn/uploads/20130515/15-015017_953.jpg",
             "http://c.hiphotos.baidu.com/zhidao/pic/item/4034970a304e251f171ee349a486c9177e3e5391.jpg"]

class cRankItem():
    def __init__(self):
        self.strAccountId = ""
        self.strNick = ""
        self.strLogo = ""
        self.iRankNum = ""
        self.iEarn = 0


class cResp():
    def __init__(self):
        self.ret = ""
        self.retDes = ""
        self.data = []


@asyncio.coroutine
def handleHttp(dictParam: dict):
    objResp = cResp()
    #objDataIns = classDataBaseMgr.getInstance()

    #测试数据
    for var in range(0,10):
        objNewItem = cRankItem()
        objNewItem.strAccountId = "{}".format(var)
        objNewItem.iRankNum = var + 1
        objNewItem.strNick = random.choice(last_names) + random.choice(first_names)
        objNewItem.strLogo = random.choice(head_urls)
        objNewItem.iEarn = random.randint(1,1000000)
        objResp.data.append(objNewItem)


    return classJsonDump.dumps(objResp)

