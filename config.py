#!/usr/bin/python
#-*-coding:utf-8-*-
'''@author:duncan'''
# 配置文件
# 目录配置
import os
project_folder_path = os.path.abspath(".." + os.path.sep + "..")
project_path = os.path.abspath("..")
stop_words_path = project_path + "/resouce/stopwords.txt"

# mysql配置
host = "localhost"
port = 3306
user = "root"
passwd = "123"
db = "TwitterUserInfo"

# mongodb配置
mongo_host = "127.0.0.1"
mongo_port = 27017

# neo4j配置
neo_host = "bolt://localhost:7687"
neo_user = "neo4j"
neo_passwd = "123"

# 参数配置
months = {'Jan':'1','Feb':'2','Mar':'3','Apr':'4','May':'5','Jun':'6','Jul':'7','Aug':'8','Sep':'9','Oct':'10','Nov':'11','Dec':'12'}


# 资源配置
# 读取停用词
def getStopWords(path):
    stopwords = set()
    with open(path,"r") as f:
        lines = f.readlines()
    for line in lines:
        stopwords.add(line.replace("\r\n","").rstrip())
    return stopwords

stopwords = getStopWords(stop_words_path)
