#!/usr/bin/python
#-*-coding:utf-8-*-
'''@author:duncan'''

import os

path = "/home/duncan/relationships/"

# 合并抓到的所有人物关系,将其他文件中的人物关系都写到relationships文件中
def Combine(path):
    files = os.listdir(path)
    with open(path + "relationships",'a') as f:
        for file in files:
            if(file != "relationships"):
                with open(path + file,'r') as ff:
                    lines = ff.readlines()
            # 将关系追加到relationships
            for line in lines:
                f.write(line)

with open(path + "relationships",'r') as f:
    lines = f.readlines()
print len(lines)


