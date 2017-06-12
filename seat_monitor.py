# coding:utf-8
# version:python3.5.1
# 作者 康雨豪
# code_version:2.0

import re
import psycopg2
import requests
import varification_decode
from bs4 import  BeautifulSoup


# 连接数据库
# 登录
# 遍历所有房间
# 将数据存入数据库

# 连接数据库
def db_connect():
    connection = psycopg2.connect(database="LibrarySeat", user="postgres",
                                  password="postgres",
                                  host="127.0.0.1",
                                  # host="139.196.243.189",
                                  port="5432")
    cursor = connection.cursor()
    return connection, cursor


# 登录网站
def login():
    cookies = get_init_page()
    get_image(cookies)
    code = varification_decode.justify_code()
    login_result = login_page(code, cookies, "2014301130041", "061236")
    while login_result is False:
        cookies = get_init_page()
        get_image(cookies)
        code = varification_decode.justify_code()
        login_result = login_page(code, cookies, "2014301130041", "061236")


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

#遍历房间
def get_room(cookies,date):
    for room in range(1,14):
        get_room_url ="http://seat.lib.whu.edu.cn/mapBook/getSeatsByRoom?room={0}&date={1}".format(room,date)
        r = requests.get(url=get_room_url, cookies=cookies, timeout=30)
        soup = BeautifulSoup(r.content, 'html.parser')

