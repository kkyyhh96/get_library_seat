# coding:utf-8
# version:python3.5.1
# 作者 康雨豪
# code_version:3.0
import datetime
import re
import time

import psycopg2
import requests
from PIL import Image

import varification_decode
from one_day import one_day

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

o = one_day()
o.db_connect()  # 连接数据库
o.query_seat()  # 获取所有人的座位


def login():
    '''
    登录
    '''
    o.all_person_login()
    print('do')

def get_seat():
    '''开始抢座'''
    o.all_person_get_seat()
    print('do after')

# BlockingScheduler
Scheduler = BlockingScheduler()
Scheduler.add_job(login, 'cron', hour=23, minute=16, second=0)  # 每天的22:25开始登录
Scheduler.add_job(get_seat, 'cron', hour=23, minute=16, second=30)  # 每天22:30开始抢座
Scheduler.start()
