#!/usr/bin/python3
import logging
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

my_sender = '2867739368@qq.com'  # 发件人邮箱账号
# my_pass = 'evvseybdkaeydcji'  # 发件人邮箱授权密码
my_pass = 'vtxrlplebcwydcjh'  # 发件人邮箱授权密码
mail_msg = """
<p>【pro竞技】尊敬的用户，您的验证码验：{}，请于5分钟内正确输入。请勿告诉其他人，如非本人操作，请忽略此短信。
"""


def send_mail(strEmail, iCode):

    try:
        msg = MIMEText(mail_msg.format(iCode), 'html', 'utf-8')
        msg['From'] = formataddr(["Pro电竞:", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(["尊敬的用户:", strEmail])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "pro电竞邮箱绑定"  # 邮件的主题，也可以说是标题

        server = smtplib.SMTP("smtp.qq.com", 587)  # 发件人邮箱中的SMTP服务器，端口是465或者587
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        senderrs = server.sendmail(my_sender, [strEmail, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        logging.info("{} {}".format(strEmail,senderrs))
        server.quit()  # 关闭连接
    except Exception as e:
        print(e)



if __name__ == "__main__":
    send_mail('2867739368@qq.com', 5556)
    print("1111")
