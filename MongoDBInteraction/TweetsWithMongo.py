#!/usr/bin/python
#-*-coding:utf-8-*-
'''@author:duncan'''

from pymongo import MongoClient
import config

# 连接文档数据库
def Conn():
    # connect to mongodb localhost
    client = MongoClient(config.mongo_host,config.mongo_port)
    # define the name of database
    db = client.twitterForTestInflu
    return db

# 根据用户id查找推文,userid是字符串格式
def getTweets(userid):
    db = Conn()
    # mongodb中没有找到该用户推文,返回None
    if(db.tweets.find({'user_id':long(userid)}).count() == 0):
        return None
    results = db.tweets.find({'user_id':long(userid)})
    return results

# 返回推文文本
def getUserTweets(userid):
    db = Conn()
    tweets = ""
    result = db.tweets.find({"user_id":long(userid)})
    for res in result:
        tweets += res["text"]
    return tweets