# coding:utf-8
# 作者 康雨豪
# version:5.0
import requests
from PIL import Image
import datetime
import time

# 获取最初的cookie
def get_init_page():
    init_url = "http://seat.lib.whu.edu.cn/login?targetUri=/"
    r = requests.get(init_url,timeout=15)
    cookies = r.cookies
    return cookies

# 获取图片及cookie
def get_image(cookies):
    im_url = "http://seat.lib.whu.edu.cn/simpleCaptcha/captcha"
    im = requests.get(im_url, cookies=cookies,timeout=15)
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
    r = requests.post(url=sign_in_url, cookies=cookies, params=params, headers=headers,timeout=30)
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
    r = requests.get(url=stay_url, cookies=cookies,headers=headers,timeout=15)
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
    r= requests.post(url=register_url, cookies=cookies, params=params,timeout=15)
    print(r.text)

cookies = None
# 个人信息在这里进行填写
username='201430113000'
password='00'
seat='0'
start='570'
end='1320'
# 开始抓取座位的时间
get_seat_hour=22
get_seat_minute=25
get_seat_minute_2=35

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
while 2>1:
    localtime=datetime.datetime.now()
    if not (localtime.hour==get_seat_hour and localtime.minute>=get_seat_minute and localtime.minute<=get_seat_minute_2):
        try:
            # 如果没有到达抢座时刻，保持停留在这个网页
            stay_page(cookies)
        except Exception as e:
            print(e)
        print("保持在线！")
        print(localtime)
        time.sleep(30)
    else:
        try:
            # 当到了抢座位的时刻，开始抢座位，每隔3s抢一次
            stay_page(cookies)
        except Exception as e:
            print(e)
        date=str(localtime.date().today()+datetime.timedelta(days=1))
        try:
            get_seat(cookies,date,seat,start,end)
        except Exception as e:
        print(date)
        print("抢座中！")
        time.sleep(3)
