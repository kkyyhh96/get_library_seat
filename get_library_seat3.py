# coding:utf-8
# version:python3.5.1
# 作者 康雨豪
# code_version:3.0
import re
import time

import psycopg2
import requests
from PIL import Image

import varification_decode
from one_day import one_day

from apscheduler.schedulers.blocking import BlockingScheduler

o = one_day()
o.db_connect()  # 连接数据库
o.query_seat()  # 获取所有人的座位


def get_seat():
    '''
    登录
    '''
    o.all_person_login()
    start = time.time()
    while True:
        o.all_person_get_seat()
        if o.is_all_get_seat():
            break
        else:
            if time.time() - start > 60 * 10:
                # 如果循环时间超过十分钟，也就是一直到22:35都还有没有抢到座位的，直接放弃。
                # TODO：如果这个时候能够发个邮件通知那些人会比较合适。个人觉得～
                break
            time.sleep(5)


# BlockingScheduler
Scheduler = BlockingScheduler()
Scheduler.add_job(get_seat, 'cron', hour=22,
                  minute=25, second=0)  # 每天的22:25开始登录
Scheduler.start()
