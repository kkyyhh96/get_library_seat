# coding:utf-8
# version:python3.5.1
# 作者 康雨豪
# code_version:6.0
import datetime
import re
import time

import requests
from PIL import Image

#获取图片
def get_image():
    im_url = "http://seat.lib.whu.edu.cn/simpleCaptcha/captcha"
    im = requests.get(im_url, timeout=15)
    with open("code.png", 'wb') as out_file:
        data = im.content
        out_file.write(data)


#提取验证码
def extract_alphabet():
    # 打开图片
    image = Image.open("code.png")
    #将图片转换为二值化图片
    image=image.convert("L")
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            pixel=image.getpixel((x,y))
            #如果像素值大于135提取为有效验证码
            if pixel>=135:
                image.putpixel((x,y),255)
            else:
                image.putpixel((x,y),0)
    image=image.convert("L")
    return image


#将验证码从左至右分为5个部分
def split_matrix_left2right(image):
    inletter = False
    foundletter = False
    start = 0
    end = 0

    letters = []

    for y in range(image.size[0]):
        for x in range(image.size[1]):
            pix = image.getpixel((y, x))
            if pix != 255:
                inletter = True
        if foundletter == False and inletter == True:
            foundletter = True
            start = y

        if foundletter == True and inletter == False:
            foundletter = False
            end = y
            letters.append((start, end))

        inletter = False
    if letters.__len__()==5:
        return True,letters
    else:
        return False,letters

def compute_vector(letters,image):
    vector=[]
    for x_start,x_end in letters:
        black=0;white=0
        size=x_end-x_start
        for x in range(x_start,x_end`):
            for y in range(image.size[1]):
                pixel=image.getpixel((x,y))
                if pixel==0:black+=1
                else:white+=1
        vector.append((size,black,white))
    return vector

get_image()
image=extract_alphabet()
result,letters=split_matrix_left2right(image)
if result==True:
    vector=compute_vector(letters,image)
    print(vector)
