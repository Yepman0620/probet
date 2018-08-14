from lib import aliyunoss2
import logging
#import requests
import urllib3



def uploadDataFileToOss(dataFile,dirPrefix,imageName):

    access_key_id = "LTAIh63z89WLm9wX"
    access_key_secret = "GNjN7MHJH61n638VdcNEgA9hNTlPGy"
    bucket_name = "probet-avator"
    endpoint = "http://oss-us-west-1.aliyuncs.com"

    # 确认上面的参数都填写正确了
    for param in (access_key_id, access_key_secret, bucket_name, endpoint):
        assert '<' not in param, '请设置参数：' + param

    # 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
    bucket = aliyunoss2.Bucket(aliyunoss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)

    try:
        bucket.put_object(dirPrefix + imageName, dataFile)
        logging.info("upload  img ToOss success！")
    except urllib3.exceptions.NewConnectionError as e:
        logging.error("upload img ToOss fail ----->{}".format(e))



