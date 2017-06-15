#!/usr/bin/python
#-*-coding:utf-8-*-
'''@author:duncan'''
import config
import time
from MySQLInteraction import TwitterWithMysql as mysql
from MongoDBInteraction import TweetsWithMongo as mongo
from DocumentClassify import TweetsClassify
from UserInterestExtract import ExtractTargetUserInterest
from UserInfluenceAnalysis import UserInfluNoPageRank
from SentimentModule import SentimentWithTime
from XMLInteraction import GenerateXML as xml
# 根据用户的userid,从mysql和mongo数据库中构建人物画像
def UserProfile(userid):
    start_time = time.time()
    if mysql.checkUser(userid) == False:
        print "数据库中不存在该用户"
        return
    user = mysql.getUserInfo(userid)
    # 获取用户推文文本
    tweets = mongo.getUserTweets(userid)
    if tweets == "":
        print "mongodb中没有该用户的推文"
        return
    print "已获取推文"

    # 获取人物所属领域
    category = TweetsClassify.Classify(tweets,config.mnb)
    user.category = category
    print "人物所属领域:%s" %  category

    # 获取人物兴趣爱好标签,两种方式
    # interests = ExtractTargetUserInterest.GenerateInterestsWithFollowers(userid)
    interests = ExtractTargetUserInterest.GenerateInterestsWithTF(userid)
    user.interest_tags = interests
    print "人物兴趣爱好标签:%s" % interests

    # 获取人物影响力分数及等级
    # rank为{1,2,3}集合中的某一元素
    influence_score,active,influ,rank = UserInfluNoPageRank.CalucateUserInfluence(userid)
    user.rank_influ = rank
    # 可以转换成中文字符串形式
    rank = config.rank_influence[rank]
    user.influenceScore = influence_score
    print "人物活跃度分数:%f,影响力度分数:%f,影响力分数:%f,影响力等级:%s" % (active,influ,influence_score,rank)

    # 获取人物心理状态,返回结果为最近一条推文起始时间,从起始时间向前一段时间内的心理状态序列以及近期心理状态结果,psy为{1,-1,0}
    # 后面后可以跟参数period,设置时间段的长度,单位为月
    starttime,psychological,psy = SentimentWithTime.SentimentWithTime(userid)
    user.psy_tweets_starttime = starttime
    user.psy = psy
    user.psy_seq = psychological
    # psy从整形转为字符串型
    psy = config.psychological[psy]
    print "人物近期心理状态:%s" % psy

    # 生成XML文档
    xml.GenerateUserXml(user)

    end_time = time.time()
    print "用时:%f" % (end_time - start_time)
# 调用接口样例
UserProfile("10047382")