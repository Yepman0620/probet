import hashlib
import logging
import random


class PwdEncrypt(object):
    """密码加密"""

    def __init__(self):
        """固定盐"""
        self.salt = "ProdjHaha94Winner"

    def create_salt(self):
        """生成随机盐"""
        salt = ''
        chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
        len_chars = len(chars) - 1
        for i in range(4):
            salt += chars[random.randint(0, len_chars)]
        return salt

    def create_md5(self, pwd):
        """密码+盐->加密"""
        try:
            h1 = hashlib.md5()
            h1.update(str(pwd).encode(encoding='utf-8'))
            strPwd = h1.hexdigest()
            h1.update((strPwd + self.salt).encode(encoding='utf-8'))
            strPassword = h1.hexdigest()
        except Exception as e:
            logging.exception(e)

        return strPassword










