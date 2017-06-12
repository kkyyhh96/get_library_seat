# -*- coding:utf-8 -*-
import requests
import datetime
import re
import logging

from pytesseract import image_to_string
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup

base_url = "http://202.114.65.179/"
login_url = base_url + "auth/signIn"
book_url = base_url + "selfRes"
captcha_url = base_url + "simpleCaptcha/captcha"
user_agent = "User-Agent:Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 " \
             "(KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"
headers = {"User-Agent": user_agent}


TODAY = datetime.datetime.today().strftime("%Y-%m-%d")
TOMORROW = (datetime.datetime.today()
            + datetime.timedelta(days=1)).strftime("%Y-%m-%d")


# getAllAvailableSeat
def ajax_search_query(offset, date=TODAY, room="null", power="null",
                      start_min="null", end_min="null"):
    return "http://202.114.65.179/freeBook/ajaxSearch?" \
           "onDate={}&building=1&room={}&hour=null&power={}&startMin={}" \
           "&endMin={}&offset={}".format(date, room, power, start_min, end_min,
                                         offset)


def get_seat(date=TOMORROW, pre_start_time=None, pre_end_time=None,
             username="2014301110161", pwd="203359", debug=False):
    s = requests.Session()
    s.headers.update(headers)

    def login():
        r = s.get(captcha_url)
        if r.headers["Content-Type"] != "image/png":
            logging.info("无法获取验证码")
            logging.info("response headers: "+r.headers["Content-Type"])
            return
        chap_img = r.content
        im = Image.open(BytesIO(chap_img)).convert("L").point(
            lambda x: 0 if x < 128 else 255)
        captcha = image_to_string(im, config="-psm {}".format(8))
        login_form = {
            "username": username,
            "password": pwd,
            "captcha": captcha}
        r = s.post(login_url, headers=headers, data=login_form)
        if r.status_code == 200 and r.url.find("login") == -1:
            logging.info("Login success")
        else:
            logging.info("captcha: "+captcha)
            logging.info("Login Failed, retrying ...")
            login()
    logging.info("{} 开始登录".format(username))
    login()
    # room_dict = {
    #     "一楼3C创客空间": 4,
    #     "一楼创新学习讨论区": 5,
    #     "二楼自然科学图书借阅区西": 6,
    #     "二楼自然科学图书借阅区东": 7,
    #     "三楼社会科学图书借阅区西": 8,
    #     "四楼图书阅览区西": 9,
    #     "三楼社会科学图书借阅区东": 10,
    #     "四楼图书阅览区东"" 11,
    #     "三楼自主学习区": 12,
    #     "3C创客-电子资源阅览区（20台）": 13, #  无电源
    #     "3C创客-双屏电脑（20台）": 14, #  无电源
    #     "创新学习-MAC电脑（12台）": 15,
    #     "创新学习-云桌面（42台）": 16
    #     }
    room_list = [10,
                 #12, 14, 13, 16, 5, 6, 7, 8, 15, 9, 4
                 ]
    # construct a tuple contain (room, power, window)
    room_list = [(i, (i != 16 or i != 13) * "1" + (i == 16 or i == 13) * "null",
                  "null") for i in room_list]
    seat_list = []  # element are tuples like: (seat_num, num, room)
    # 根据特定的房间来请求数据
    for room in room_list:
        search_form = {
            "onDate": date,  # ''(default today) or YYYY-MM-DD
            "building": "1",
            "room": room[0],  # null or int
            "hour": "null",  # null or int
            "startMin": pre_start_time,  # int % 15 == 0
            "endMin": pre_end_time,  # int % 15 == 0
            "power": room[1],  # 1 or 0 or null
            "window": room[2]}  # 1 or 0 or null
        r = s.post(base_url + "freeBook/ajaxSearch", data=search_form)
        while True:
            offset = r.json()["offset"]
            # seatNum = r.json()["seatNum"]
            seat_str = r.json()["seatStr"]
            soup = BeautifulSoup(seat_str, 'lxml')
            for i in soup.findAll('li', title="座位空闲"):

                seat_list.append((i['id'], i.text.replace('\n', '')[:3],
                                 i.text.replace('\n', '')[3:]))
            if offset == -1:
                break
            r = s.get(ajax_search_query(offset=offset,
                                        date=search_form["onDate"],
                                        room=search_form["room"],
                                        power=search_form["power"],
                                        start_min=search_form["startMin"],
                                        end_min=search_form["endMin"]))
    logging.info("Got {} seats.".format(len(set(seat_list))) +
                 " Trying to book seat...")

    if debug:
        logging.info("Seat list: "+str(seat_list))
    if seat_list:
        if debug:
            seat_list = seat_list[:5]
        for seat in seat_list:
            # Book one seat
            seat_id = seat[0][-4:]
            if pre_start_time is None and pre_end_time is None:
                get_time_url = base_url + "freeBook/ajaxGetTime"
                get_end_time_url = base_url + "freeBook/ajaxGetEndTime"
                start_form_data = {
                    "id": seat_id,
                    "date": date
                }
                r = s.post(get_time_url, data=start_form_data)
                try:
                    start_time = re.findall('time="(?P<time>\d+?)"', r.text)[0]
                except IndexError:
                    logging.info("Cannot find start time available,"
                                 " the response is: ")
                    logging.info(r.text)
                    continue
                end_form_data = {
                    "start": start_time,
                    "seat": seat_id,
                    "date": date
                }
                if debug:
                    logging.info("end_form data:"+str(end_form_data))
                r = s.post(get_end_time_url, data=end_form_data)
                try:
                    end_time = re.findall('time="(?P<time>\d+?)"', r.text)[-1]
                except IndexError:
                    logging.info("Cannot find end time available,"
                                 " the response is: ")
                    continue
            else:
                start_time = pre_start_time
                end_time = pre_end_time
            book_form = {"date": search_form["onDate"],  # YYYY-MM-DD
                         "seat": seat_id,  # \d{4}
                         "start": start_time,  # now or int % 15 == 0
                         "end": end_time,  # int % 15 == 0
                         "captcha": ""}
            if debug:
                logging.info(book_form)
                continue
            r = s.post(book_url, book_form)
            soup = BeautifulSoup(r.text, 'lxml')
            result = '\n'.join(tag.text.replace("\xa0", '') for tag in soup.find_all('dd'))
            if result.find("预约失败") == -1:
                logging.info(username+"\n"+result)
                print(username, result)
                break
            logging.info(username, result)
            print(username, result)
            logging.info("正在尝试下一个座位")
    else:
        logging.info("未找到座位")

if __name__ == "__main__":
    """get_seat(date=TODAY,
       start_time="now",
       end_time=1050,
       username="2014301110161",
       pwd="203359")

       date can be either of TODAY, TOMORROW.
       """
    get_seat(debug=True)
