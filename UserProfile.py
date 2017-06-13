#!/usr/bin/python
#-*-coding:utf-8-*-
'''@author:duncan'''
from MongoDBInteraction import TweetsWithMongo as mongo

# 根据用户的userid,从mysql和mongo数据库中构建人物画像
def UserProfile(userid):
    pass

print mongo.getUserById("95955871")
