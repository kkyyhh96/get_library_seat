# coding:utf-8
# version:python3.5.1
# 作者 康雨豪
# code_version:3.0

import datetime

import psycopg2

from person import person


class one_day(object):
    '''
    一天中应该执行的所有的操作
    '''
    def __init__(self):
        '''
        获取第二天的日期
        '''
        self.date = str(datetime.datetime.now().date().today()
                        + datetime.timedelta(days=1))
        self.start_hour = 22
        self.start_time = 25
        self.end_time = 35
        self.user = []

    # 连接数据库
    def db_connect(self):
        self.connection = psycopg2.connect(database="LibrarySeat", user="postgres",
                                           password="postgres",
                                           # host="127.0.0.1",
                                           host="139.196.243.189",
                                           port="5432")
        self.cursor = self.connection.cursor()

    # 查询每个人的座位信息
    def query_seat(self):
        try:
            sql_command_select = "SELECT * FROM seat"
            self.cursor.execute(sql_command_select)
            users = self.cursor.fetchall()
            for data in users:
                # 获取每一个用户的座位信息
                try:
                    print(data[0])
                    self.user.append(
                        person(str(data[0]),
                               str(data[1]),
                               str(data[2]),
                               str(self.date),
                               str(data[3]),
                               str(data[4])))
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
            self.connection.rollback()

    def all_person_login(self):
        '''
        # 推荐写法
        for u in self.users:
            try:
                u.login_main()
                print('{} login successed!'.format(u.username))
            except Exception as e:
                print('{} login failed : {}'.format(u.username, str(e)))
        '''
        for u in self.user:
            try:
                u.login_main()
            except Exception as e:
                print(e)

    def all_person_get_seat(self):
        for u in self.user:
            try:
                u.get_seat()
            except Exception as e:
                print(e)




