'''
处理和用户相关的操作
'''
# coding:utf-8
# version:python3.5.1
# 作者 康雨豪
# code_version:3.0
import re

import requests
from PIL import Image

import varification_decode


class person(object):
    '''
    应该对每个函数和类都注释一下～
    按照google的编码规范（也是python之父推荐的编码规范，所有的类名都应该首字母大写）
    '''

    def __init__(self, username, password, seat, date, start_time, end_time):
        self.username = username  # 用户名
        self.password = password  # 用户密码
        self.seat = seat  # 用户座位号
        self.date = date  # 抢座日期
        self.start_time = start_time  # 开始时间
        self.end_time = end_time  # 结束时间
        self.if_get_seat = False  # 判断是否获取了座位

    def get_init_page(self):
        '''
        获取最初的cookie
        '''
        init_url = "http://seat.lib.whu.edu.cn/login?targetUri=/"
        r = requests.get(init_url, timeout=15)
        cookies = r.cookies
        self.cookies = cookies

    def get_image(self):
        """
        获取图片及cookie
        """
        im_url = "http://seat.lib.whu.edu.cn/simpleCaptcha/captcha"
        im = requests.get(im_url, cookies=self.cookies, timeout=5)
        with open("image.png", 'wb') as out_file:
            data = im.content
            out_file.write(data)
        # 打开图片
        image = Image.open("image.png")
        image.close()
        self.code = varification_decode.justify_code()

    # 登录系统
    def login_page(self):
        # 个人信息
        params = dict(username=str(self.username),
                      password=str(self.password),
                      captcha=self.code)
        # 登录
        headers = {
            "Connection": "keep-alive"
        }
        sign_in_url = "http://seat.lib.whu.edu.cn/auth/signIn"
        r = requests.post(url=sign_in_url,
                          cookies=self.cookies,
                          params=params, headers=headers, timeout=3)
        # TODO:这个地方应该检查是否操作成功。
        login_word = re.findall(r'{0}'.format(
            "我的预约").encode('utf-8'), r.text.encode('utf-8'))
        # 判断是否登录成功
        if login_word.__len__() > 0:
            return True
        else:
            return False

    def login_main(self):
        '''
        登录主函数
        '''
        self.get_init_page()
        self.get_image()
        count = 0
        while self.login_page() is False:
            self.get_init_page()
            self.get_image()
            count = count + 1
            # 八次登陆不上去就跳过
            if count >= 8:
                break

    # 预定座位
    def get_seat(self):
        if self.if_get_seat is False:
            register_url = "http://seat.lib.whu.edu.cn/selfRes"
            params = {
                'date': str(self.date),
                'seat': str(self.seat),
                'start': str(self.start_time),
                'end': str(self.end_time)
            }
            r = requests.post(url=register_url,
                              cookies=self.cookies, params=params, timeout=2)
            get_seat_word = re.findall(r'{0}'.format(
                "系统已经为您预定").encode('utf-8'), r.text.encode('utf-8'))
            # 判断是否抢座成功
            if get_seat_word.__len__() > 0:
                self.if_get_seat = True
                print("{0}抢座成功!{1}".format(str(self.username), str(self.date)))
            else:
                print('{0}抢座失败!{1}'.format(str(self.username), str(self.date)))
# p=person("2014301130041","987456","6163","2017-06-12","810","840")
# p.login_main() #登录
# p.get_seat() #获取座位
