#!/usr/bin/python
#-*-coding:utf-8-*-
'''@author:duncan'''
import config
from MongoDBInteraction import TweetsWithMongo as mongo
from DocumentClassify import TweetsClassify
from UserInterestExtract import ExtractTargetUserInterest
from UserInfluenceAnalysis import UserInfluNoPageRank
from SentimentModule import SentimentWithTime
# 根据用户的userid,从mysql和mongo数据库中构建人物画像
def UserProfile(userid):
    pass
    # 获取用户推文文本
    tweets = mongo.getUserTweets(userid)
    print "已获取推文"

    # 获取人物所属领域
    category = TweetsClassify.Classify(tweets)
    print "人物领域已分类"

    # 获取人物兴趣爱好标签,两种方式
    interests = ExtractTargetUserInterest.GenerateInterestsWithFollowers(userid)
    # interests = ExtractTargetUserInterest.GenerateInterestsWithTF(userid)
    print "人物兴趣标签形成"

    # 获取人物影响力分数及等级
    # rank为{1,2,3}集合中的某一元素
    influence_score,rank = UserInfluNoPageRank.CalucateUserInfluence(userid)
    # 可以转换成中文字符串形式
    rank = config.rank_influence[rank]
    print "影响力评分评级完毕"

    # 获取人物心理状态,返回结果为最近一条推文起始时间,从起始时间向前一段时间内的心理状态序列以及近期心理状态结果,psy为{1,-1,0}
    # 后面后可以跟参数period,设置时间段的长度,单位为月
    starttime,psychological,psy = SentimentWithTime.SentimentWithTime(userid)
    print "人物心理状态评定完毕"