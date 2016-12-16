# coding:utf-8
# 作者 康雨豪
import requests
from PIL import Image
import datetime
import time

# 获取最初的cookie
def get_init_page():
    init_url = "http://seat.lib.whu.edu.cn/login?targetUri=/"
    r = requests.get(init_url)
    cookies = r.cookies
    return cookies

# 获取图片及cookie
def get_image(cookies):
    im_url = "http://seat.lib.whu.edu.cn/simpleCaptcha/captcha"
    im = requests.get(im_url, cookies=cookies)
    with open("image.png", 'wb') as out_file:
        data = im.content
        out_file.write(data)
    # 打开图片
    image = Image.open("image.png")
    image.show()

def login_page(code, cookies,username,password):
    # 个人信息
    params = dict(username=str(username), password=str(password), captcha=code)

    # 登录
    headers = {
        "Connection": "keep-alive"
    }
    sign_in_url = "http://seat.lib.whu.edu.cn/auth/signIn"
    r = requests.post(url=sign_in_url, cookies=cookies, params=params, headers=headers)
    if r.url == 'http://seat.lib.whu.edu.cn/':
        return True;
    else:
        return False;

# 保持停留
def stay_page(cookies):
    stay_url = "http://seat.lib.whu.edu.cn/"
    headers = {
        "Connection": "keep-alive"
    }
    r = requests.get(url=stay_url, cookies=cookies,headers=headers)
    print(r.text)
    return r

# 预定座位
def get_seat(cookies, date, seat, start, end):
    register_url = "http://seat.lib.whu.edu.cn/selfRes"
    params = {
        'date': str(date),
        'seat': str(seat),
        'start': str(start),
        'end': str(end)
    }
    r= requests.post(url=register_url, cookies=cookies, params=params)
    print(r.text)

cookies = None
# 个人信息在这里进行填写
username='20143011300'
password='0'
date='2016-12-17'
seat='6152'
start='540'
end='1320'
# 开始抓取座位的时间
get_seat_hour=22
get_seat_minute=25

cookies = get_init_page()
get_image(cookies)
valid_code = input("请输入验证码:\n")

login_success=login_page(valid_code, cookies,username,password)
while not login_success:
    print("登陆错误！请重新输入验证码！")
    cookies = get_init_page()
    get_image(cookies)
    valid_code = input("请输入验证码\n")
    login_success = login_page(valid_code, cookies, username, password)

print("登陆成功！")

# 开始抢座位
localtime=datetime.datetime.now()
while not (localtime.hour>=get_seat_hour and localtime.minute>=get_seat_minute):
    # 如果没有到达抢座时刻，保持停留在这个网页
	stay_page(cookies)
	localtime = datetime.datetime.now()
	print(localtime)
	time.sleep(30)
else:
# 当到了抢座位的时刻，开始抢座位，每隔5s抢一次
    count=1
    while count<300:
        stay_page(cookies)
        get_seat(cookies,date,seat,start,end)
        print("抢座中！")
        count=count+1
        time.sleep(5)
