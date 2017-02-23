# coding:utf-8
# version:python3.5.1
# 作者 康雨豪
# code_version:6.0
import os

from PIL import Image


# 遍历训练集中的图片
def walk_img(code_file):
    path = ".\dataset"
    try:
        for pathName, noFile, file in os.walk(path):
            for images in file:
                img_path = pathName + "\\" + images
                im = Image.open(img_path)
                vector=compute_vector(im)
                code_file.writelines("{0},{1},{2},{3},{4},{5}\n".format(str(images).split('.')[0],vector[0],vector[1],vector[2],
                                                                        vector[3],vector[4]))
    except Exception as e:
        print(e)


# 计算特征向量
def compute_vector(image):
    vector = []
    black = 0
    white = 0
    black_half=0
    white_half=0
    for x in range(image.size[0]):
        if x==int(image.size[0]/2):
            black_half=black
            white_half=white
        for y in range(image.size[1]):
            pixel = image.getpixel((x, y))
            if pixel == 0:
                black += 1
            else:
                white += 1
    vector.append(image.size[0])
    vector.append(black)
    vector.append(white)
    vector.append(black_half)
    vector.append(white_half)
    return vector

file=open('code_vector.txt','a')
walk_img(file)
file.close()
