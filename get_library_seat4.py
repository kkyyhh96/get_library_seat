# coding:utf-8
# version:python3.5.1
# 作者 康雨豪
# code_version:4.0
import datetime
import re
import time
import os

import requests
from PIL import Image
import multiprocessing

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
    # 保存图片
    with open("image.png", 'wb') as out_file:
        data = im.content
        out_file.write(data)


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
    try:
        requests.post(url=register_url, cookies=cookies, params=params, timeout=10)
        print(os.getpid())
    except requests.exceptions.ConnectionError as e:
        print(e)
    finally:
        pass


def Login():
    while True:
        # 获取cookies
        cookies = get_init_page()
        # 获取验证码并填写
        get_image(cookies)
        valid_code = varification_decode.justify_code()
        # 登录
        login_success = login_page(valid_code, cookies, username, password)
        if login_success == True:
            print("登陆成功！")
            break
    return cookies


# 主要步骤
if __name__ == '__main__':
    # 个人信息在这里进行填写
    username = '20143011300'
    password = '98'
    seat = '25'
    start = '750'
    end = '1050'
    # 开始抓取座位的时间
    get_seat_hour = 22
    get_seat_minute = 25
    get_seat_minute_2 = 35

    # 开始抢座位
    while True:
        try:
            # 登录
            cookies = Login()
            localtime = datetime.datetime.now()
            # 没有到抢座时间
            while not (
                                localtime.hour == get_seat_hour and localtime.minute >= get_seat_minute and localtime.minute <= get_seat_minute_2):
                while True:
                    # 保持停留
                    stay_status = stay_page(cookies)
                    if stay_status is not True:
                        cookies = Login()
                    else:
                        time.sleep(120)
                        break
            else:
                # 到了抢座时间
                try:
                    pool = multiprocessing.Pool(4)
                    while True:
                        date = str(localtime.date().today() + datetime.timedelta(days=1))
                        pool.apply(get_seat, args=(cookies, date, seat, start, end))
                        if localtime.minute >= get_seat_minute_2:
                            break
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
