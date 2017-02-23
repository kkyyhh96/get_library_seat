# coding:utf-8
# version:python3.5.1
# 作者 康雨豪
# code_version:8.0
import datetime
import re
import time

import psycopg2
import requests
from PIL import Image

import varification_decode


# 获取最初的cookie
def get_init_page():
    init_url = "http://seat.lib.whu.edu.cn/login?targetUri=/"
    r = requests.get(init_url, timeout=15)
    cookies = r.cookies
    return cookies


# 获取图片及cookie
def get_image(cookies):
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
def login_page(code, cookies, username, password):
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


# 保持停留
def stay_page(cookies):
    stay_url = "http://seat.lib.whu.edu.cn/"
    headers = {
        "Connection": "keep-alive"
    }
    r = requests.get(url=stay_url, cookies=cookies, headers=headers, timeout=15)
    stay_word = re.findall(r'{0}'.format("我的预约").encode('utf-8'), r.text.encode('utf-8'))
    # 判断是否仍然停留
    if stay_word.__len__() > 0:
        return True
    else:
        return False


# 预定座位
def get_seat(cookies, date, seat, start, end):
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


# 连接数据库
def db_connect():
    connection = psycopg2.connect(database="LibrarySeat", user="postgres",
                                  password="postgres", host="127.0.0.1", port="5432")
    cursor = connection.cursor()
    return connection, cursor


# 查询座位信息
def query_seat(connection, cursor, username):
    try:
        sql_command_select = "SELECT seat,start_time,end_time FROM seat WHERE username={0};".format(username)
        cursor.execute(sql_command_select)
        data = cursor.fetchone()
        try:
            seat = str(data).split(',')[0].split('(')[1]
            start_time = str(data).split(',')[1]
            end_time = str(data).split(',')[2].split(')')[0]
            return seat, start_time, end_time
        except Exception:
            return None, None, None
    except Exception as e:
        print(e)
        connection.rollback()


# 主要步骤
def __main__():
    # 个人信息在这里进行填写
    username = '20143011300'
    password = '06'
    seat = '8'
    start = '570'
    end = '1320'
    # 开始抓取座位的时间
    get_seat_hour = 22
    get_seat_minute = 25
    get_seat_minute_2 = 35

    # 连接数据库
    connect, cursor = db_connect()
    seat, start, end = query_seat()
    # 登录
    cookies = get_init_page()
    get_image(cookies)
    # valid_code = input("请输入验证码:\n")
    valid_code = varification_decode.justify_code()
    print(valid_code)
    login_success = login_page(valid_code, cookies, username, password)
    while not login_success:
        print("登陆错误！请重新输入验证码！")
        cookies = get_init_page()
        get_image(cookies)
        # valid_code = input("请输入验证码\n")
        valid_code = varification_decode.justify_code()
        print(valid_code)
        login_success = login_page(valid_code, cookies, username, password)

    print("登陆成功！")

    # 开始抢座位
    while 2 > 1:
        localtime = datetime.datetime.now()
        if not (
                            localtime.hour == get_seat_hour and localtime.minute >= get_seat_minute and localtime.minute <= get_seat_minute_2):
            try:
                # 如果没有到达抢座时刻,保持停留在这个网页
                if stay_page(cookies) is False:
                    print("需要重新登录!")
                    break
            except Exception as e:
                print(e)
            print("保持在线！" + str(localtime))
            seat, start, end = query_seat()
            # 保持停留的时间
            time.sleep(3)
        else:
            try:
                # 当到了抢座位的时刻,开始抢座位,每隔3s抢一次
                stay_page(cookies)
            except Exception as e:
                print(e)
            date = str(localtime.date().today() + datetime.timedelta(days=1))
            try:
                if get_seat(cookies, date, seat, start, end):
                    print(str(date) + "抢座成功！")
                    continue
                else:
                    print(str(date) + "抢座中！")
            except Exception as e:
                print(e)
            time.sleep(3)
    __main__()


__main__()
