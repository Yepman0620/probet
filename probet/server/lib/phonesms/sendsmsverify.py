from lib.aliyunsdkcore.client import AcsClient
from lib.aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest

import uuid

REGION = "cn-hangzhou"  # 暂时不支持多region

ACCESS_KEY_ID = "LTAIh63z89WLm9wX"
ACCESS_KEY_SECRET = "GNjN7MHJH61n638VdcNEgA9hNTlPGy"


appid = 1400117029  # SDK AppID是1400开头
# 短信应用SDK AppKey
appkey = "18f3a24e4f65ecab391673d191227ffc"


acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)

# from qcloudsms_py import SmsSingleSender
# from qcloudsms_py.httpclient import HTTPError



def send_sms(phone_number, code):

    #阿里云的

    smsRequest = SendSmsRequest.SendSmsRequest()

    smsRequest.set_TemplateCode("SMS_136600002")

    smsRequest.set_TemplateParam("{\"code\":\"%d\"}" % code)

    smsRequest.set_OutId(uuid.uuid1())

    smsRequest.set_SignName("Esports007")

    smsRequest.set_PhoneNumbers(phone_number)

    smsResponse = acs_client.do_action_with_exception(smsRequest)
    return smsResponse
    #
    # sms_type = 0  # Enum{0: 普通短信, 1: 营销短信}
    # ssender = SmsSingleSender(appid, appkey)
    # try:
    #     result = ssender.send(sms_type, 86, phone_number,
    #                           "【pro竞技】尊敬的用户，您的验证码{},请于5分钟内正确输入。请勿告诉其他人，如非本人操作，请忽略此短信。".format(code), extend="", ext="")
    #
    #     print(result)
    # except HTTPError as e:
    #     return '{"code":"Falied","Message":"发送短信出错，请稍后再试"}'
    # except Exception as e:
    #     return '{"code":"Falied","Message":"发送短信出错，请稍后再试"}'

    #return result
