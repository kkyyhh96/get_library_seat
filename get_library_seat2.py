# coding:utf-8
# version:python3.5.1
# 作者 康雨豪
# code_version:2.0
import datetime
import re
import time

import psycopg2
import requests
from PIL import Image

import varification_decode


# 用户类
class user_seat(object):
    def __init__(self, username, password, seat, start_time, end_time):
        self.username = username
        self.password = password
        self.seat = seat
        self.start_time = start_time
        self.end_time = end_time

    # 抢座总程序
    def get_seat_main(self):
        # 获取最初的cookie
        cookies = self.get_init_page()
        # 根据最初的cookie获取验证码
        self.get_image(cookies)
        # 识别验证码
        code = varification_decode.justify_code()
        # 登录网页
        login_result = self.login_page(code, cookies, self.username, self.password)
        # 当登录失败的时候,重新登录
        while login_result is False:
            cookies = self.get_init_page()
            self.get_image(cookies)
            code = varification_decode.justify_code()
            login_result = self.login_page(code, cookies, self.username, self.password)
        print("登陆成功！")
        # 发送抢座请求
        # 获取当前日期
        localtime = datetime.datetime.now()
        # 获取第二天的日期
        date = str(localtime.date().today() + datetime.timedelta(days=1))
        get_seat_result = self.get_seat(cookies, date, self.start_time, self.end_time, self.seat)
        if get_seat_result is True:
            print("抢座成功！{0}".format(self.username))

    # 获取最初的cookie
    def get_init_page(self):
        init_url = "http://seat.lib.whu.edu.cn/login?targetUri=/"
        r = requests.get(init_url, timeout=15)
        cookies = r.cookies
        return cookies

    # 获取图片及cookie
    def get_image(self, cookies):
        im_url = "http://seat.lib.whu.edu.cn/simpleCaptcha/captcha"
        im = requests.get(im_url, cookies=cookies, timeout=15)
        with open("image.png", 'wb') as out_file:
            data = im.content
            out_file.write(data)
        # 打开图片
        image = Image.open("image.png")
        # image.show()
        image.close()

    # 登录系统
    def login_page(self, code, cookies, username, password):
        # 个人信息
        params = dict(username=str(username), password=str(password), captcha=code)

        # 登录
        headers = {
            "Connection": "keep-alive"
        }
        sign_in_url = "http://seat.lib.whu.edu.cn/auth/signIn"
        r = requests.post(url=sign_in_url, cookies=cookies, params=params, headers=headers, timeout=30)
        login_word = re.findall(r'{0}'.format("我的预约").encode('utf-8'), r.text.encode('utf-8'))
        # 判断是否登录成功
        if login_word.__len__() > 0:
            return True
        else:
            return False

    # 预定座位
    def get_seat(self, cookies, date, seat, start, end):
        register_url = "http://seat.lib.whu.edu.cn/selfRes"
        params = {
            'date': str(date),
            'seat': str(seat),
            'start': str(start),
            'end': str(end)
        }
        r = requests.post(url=register_url, cookies=cookies, params=params, timeout=2)
        get_seat_word = re.findall(r'{0}'.format("系统已经为您预定好了座位").encode('utf-8'), r.text.encode('utf-8'))
        # 判断是否抢座成功
        if get_seat_word.__len__() > 0:
            return True
        else:
            return False


class get_library_seat2(object):
    def __init__(self):
        # 设置每天抢座位的时刻
        self.start_hour = 22
        self.start_time_minute = 24
        self.end_time_minute = 33

        # 抢座总程序

    def get_seat(self):
        while 2 > 1:
            time_now = datetime.datetime.now()
            # 如果没有到抢座时间,停止4分钟
            if not (
                                time_now.hour == self.start_hour and time_now.minute >= self.start_time_minute and time_now.minute >= self.start_time_minute):
                time.sleep(240)
            else:
                #如果到达了抢座的时间,连接数据库并进行抢座
                connection,cursor=self.db_connect()
                self.query_seat(connection,cursor)
                time.sleep(1)

    # 连接数据库
    def db_connect(self):
        connection = psycopg2.connect(database="LibrarySeat", user="postgres",
                                      password="postgres", host="139.196.243.189", port="5432")
        cursor = connection.cursor()
        return connection, cursor

    # 查询每个人的座位信息
    def query_seat(self, connection, cursor):
        try:
            sql_command_select = "SELECT * FROM seat"
            cursor.execute(sql_command_select)
            users = cursor.fetchall()
            for data in users:
                # 获取每一个用户的座位信息
                try:
                    username = str(data).split(',')[0].split('(')[1]
                    password = str(data).split(',')[1].split('\'')[1]
                    seat = str(data).split(',')[2]
                    start_time = str(data).split(',')[3]
                    end_time = str(data).split(',')[4].split(')')[0]
                    user = user_seat(username, password, seat, start_time, end_time)
                    # 为该用户抢座
                    user.get_seat_main()
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
            connection.rollback()


get_library_seat2_test=get_library_seat2()
get_library_seat2_test.get_seat()