# coding:utf-8
# version:python3.5.1
# 作者 康雨豪
# code_version:7.0

import requests
from PIL import Image


# 获取图片
def get_image():
    im_url = "http://seat.lib.whu.edu.cn/simpleCaptcha/captcha"
    im = requests.get(im_url, timeout=15)
    try:
        # 写入图片
        with open("image.png", 'wb') as out_file:
            data = im.content
            out_file.write(data)
    except Exception as e:
        print(e)


# 提取验证码
def extract_alphabet():
    # 打开图片
    image = Image.open("image.png")
    # 将图片转换为二值化图片
    image = image.convert("L")
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            pixel = image.getpixel((x, y))
            # 如果像素值大于135提取为有效验证码
            if pixel >= 135:
                image.putpixel((x, y), 255)
            else:
                image.putpixel((x, y), 0)
    image = image.convert("L")
    return image


# 将验证码从左至右分为5个部分
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

    # 如果验证码分为了5个部分则成功
    if letters.__len__() == 5:
        return True, letters
    else:
        return False, letters


# 计算特征向量
def compute_vector(letters, image):
    string_list = []
    vector = []
    for x_start, x_end in letters:
        black = 0
        white = 0
        black_half = 0
        white_half = 0
        size = x_end - x_start
        im = Image.new('L', (size, 51), 255)
        for x in range(x_start, x_end):
            if x == int((x_start + x_end) / 2):
                black_half = black
                white_half = white
            for y in range(image.size[1]):
                pixel = image.getpixel((x, y))
                if pixel == 0:
                    black += 1
                    im.putpixel((x - x_start, y), 0)
                else:
                    white += 1
                    im.putpixel((x - x_start, y), 255)
        vector.append(size)
        vector.append(black)
        vector.append(white)
        vector.append(black_half)
        vector.append(white_half)
        string_list.append(match_code(vector))
        vector = []
        # 获取训练集的图片
        # im.save("./dataset/{0}.png".format(x_start),"png")
        # 返回具体的字符
    return string_list


# 匹配字符
def match_code(vector):
    file = open('code_vector.txt', 'r')
    match_str = ''
    match_rate = 5000
    for line in file.readlines():
        string = line.split(',')[0]
        size = line.split(',')[1]
        black = line.split(',')[2]
        white = line.split(',')[3]
        black_half = line.split(',')[4]
        white_half = line.split(',')[5]
        # 计算特征向量
        square = (lambda x, y: (x - y) * (x - y))
        rate = square(int(size), vector[0]) + 0.1 * square(int(black), vector[1]) + 0.1 * square(int(white), vector[2])
        rate += 0.1 * square(int(black_half), vector[3]) + 0.1 * square(int(white_half), vector[4])
        if rate < match_rate:
            match_rate = rate
            match_str = string
    file.close()
    return match_str


# 识别验证码
def justify_code():
    try:
        image = extract_alphabet()
        result, letters = split_matrix_left2right(image)
        # 如果分割成为了5个字符
        if result == True:
            # 计算特征向量
            vector = compute_vector(letters, image)
            code = ""
            for string in vector:
                code += str(string)
            return code
        else:
            return None
    except Exception as e:
        print(e)

# get_image()
# image = extract_alphabet()
# result, letters = split_matrix_left2right(image)
## 如果分割成为了5个字符
# if result == True:
#    # 计算特征向量
#    vector = compute_vector(letters, image)
# justify_code()
