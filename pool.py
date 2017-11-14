import multiprocessing
import requests

def task(x,y):
    init_url = "http://seat.lib.whu.edu.cn/login?targetUri=/"
    requests.get(init_url, timeout=15)
    print("{0},{1}".format(x,y))

if __name__ == '__main__':
    p=multiprocessing.Pool(4)
    for i in range(1000000):
        p.apply(task,args=(i,i+5))

