#!/usr/bin/python
#-*-coding:utf-8-*-
'''@author:duncan'''

import os
import re
import nltk
from pytagcloud import create_tag_image,make_tags
import webbrowser
import math
import time
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from numpy import *
import config

BeatFactor = 3000000

project_path = config.project_path
project_folder_path = config.project_folder_path
followers_file_path = project_folder_path + "/TweetsSamples/"
target_tweets_path = project_folder_path + "/TweetsSamples/"

# usercandidate = []

# 读取停用词
def getStopWords(path):
    stopwords = set()
    with open(path,"r") as f:
        lines = f.readlines()
    for line in lines:
        stopwords.add(line.replace("\r\n","").rstrip())
    return stopwords

stopwords = getStopWords(config.stop_words_path)

def PreProcess(text):
    # open_file = open(slang_file_path,"rb")
    # slang = pickle.load(open_file)
    # open_file.close()

    # clear @/#/http
    text = re.sub(r'[@|#][\d|\w|_]+|http[\w|:|.|/|\d]+',"",text)
    # print text
    wordslist = []
    if text == "" or text == None:
        return []
    words = word_tokenize(text)
    # clear @/#/url/emotion
    for word in words:
        # count = 0
        if word not in stopwords:
            # if word in slang:
            # 	count += 1
            # 	print count
            #     word = slang[word]
            #     subwords = word.split(" ")
            #     for subword in subwords:
            #         if subword not in (stopwords.words("english") and twitter_stop_words):
            #             # 转换成小写
            #             wordslist.append(subword.lower())
            # else:
            if len(word) > 2 and word.isalpha():
                wordslist.append(word.lower())
    try:
        pos = nltk.pos_tag(wordslist)
    # wordlist = [ps.stem(w[0],w[1]) for w in pos]
    # pos = nltk.pos_tag(wordslist)
    except Exception as e:
        pos = []
    return pos

'''
步骤2：兴趣词或短语生成候选集
兴趣词的模式为
单个词形式：Noun|Adjective|Verb (经测试效果不是很好，暂时选用名词Noun形式)
词组形式：(Verb?)(Adjective|Noun)Noun+ (词组形式暂时选用动词+名词 或  形容词+名词形式)
动词和名词先做词性还原
'''
def Generation(pos):
    if len(pos) < 1:
        return []
    usercandidate = []
    # global usercandidate
    multicandidate = []
    lemmatizer = WordNetLemmatizer()
    single_pattern = ["N","J","V"]
    for w in pos:
        word = ""
        # if w[1][0] in single_pattern:
        # if w[1][0] == 'V':
        #     # 排除前100常用的动词
        #     word = lemmatizer.lemmatize(w[0],'v')
        #     if word in topverbwords:
        #         continue
        if(w[1][0] == 'N'):
            word = lemmatizer.lemmatize(w[0])
        # else:
        #     word = lemmatizer.lemmatize(w[0],'a')
            usercandidate.append(word)
    i = 0
    while(i < len(pos) - 2):
        phase = ""
        # verb + adj + n+ or verb n+
        if (pos[i])[1][0] == 'V' and (pos[i + 1][1][0] == 'N' or (pos[i + 1][1][0] == "J" and pos[i + 2][1][0] == "N")):
            if pos[i + 1][1][0] == 'N':
                suffix = lemmatizer.lemmatize(pos[i + 1][0],'a')
            else:
                suffix = lemmatizer.lemmatize(pos[i + 1][0],'n')
            phase += lemmatizer.lemmatize((pos[i])[0],'v') + " " + suffix
            i = i + 2
            while(i < len(pos) and (pos[i])[1][0] == 'N'):
                phase += " " + lemmatizer.lemmatize((pos[i])[0])
                i += 1
            multicandidate.append(phase)
        # adj + n+
        elif(pos[i][1][0] == "J" and pos[i + 1][1][0] == "N"):
            if((i !=0 and pos[i - 1 ][1][0] != "V") or i == 0):
                phase +=lemmatizer.lemmatize((pos[i])[0],"a") + " " + lemmatizer.lemmatize((pos[i + 1])[0])
                i += 2
                while(i < len(pos) and (pos[i])[1][0] == 'N'):
                    phase += " " + lemmatizer.lemmatize((pos[i])[0],"n")
                    i += 1
            multicandidate.append(phase)
        # n n+
        # elif(pos[i][1][0] == "N" and pos[i + 1][1][0] == "N"):
        #     if((i != 0 and pos[i - 1][1][0] != "V" and pos[i - 1][1][0] != "J") or i ==0):
        #         phase += lemmatizer.lemmatize((pos[i])[0]) + " " + lemmatizer.lemmatize((pos[i + 1])[0])
        #         i += 2
        #         while(i < len(pos) and (pos[i])[1][0] == 'N'):
        #             phase += " " + lemmatizer.lemmatize((pos[i])[0])
        #             i += 1
        #     MultiCandidate.append(phase)
        else:
            i += 1
        if len(multicandidate) != 0:
            usercandidate += multicandidate
        return usercandidate

'''
步骤3：候选集排序
单用户使用TF词频排序,并生成前NS兴趣候选集
'''
def CalculateTF(usercandidate):
    vac = set(usercandidate)
    vacdic = {}
    # 得到词频
    for phase in vac:
        vacdic[phase] = usercandidate.count(phase)
    sum = 0
    for key in vacdic.keys():
        sum += vacdic[key]
    # 计算TF值
    for key in vacdic.keys():
        vacdic[key] = vacdic[key] * 1.0 / sum

    # 按照键值排序
    vacdic = sorted(vacdic.items(),key = lambda dic:dic[1],reverse = True)
    # 输出前100个兴趣候选集
    return vacdic[:50]

def getUserTopInterest(path,screen_name):
    # global usercandidate
    usercandidate = []
    with open(path + screen_name,"r") as f:
        lines = f.readlines()
        for line in lines:
            # 移除回复/对话的推文 （是以@XXXX开头）
            if re.match(r"""^["|.]?@[\w|_]+""",line) == None:
                line.replace("\n","")
                # print "user tweet id is %d" % user_tweet_id
                res = Generation(PreProcess(line.decode("utf-8")))
                # Generation(PreProcess(line.decode("utf-8")))
                if res != None:
                    usercandidate += res
    usercandidate = CalculateTF(usercandidate)
    return usercandidate

'''
步骤4:得到目标用户候选集后，在其Followers中计算TFIDF值
'''
def CalculateTFIDF(usercandidate,followers_file_path):
    followers_tweets = os.listdir(followers_file_path)
    userNumber = len(followers_tweets)
    print "该用户有%d个粉丝,现在开始计算" % (userNumber - 1)
    tfidf = [1 for i in range(50)]
    # for i in range(100):
    #     tfidf.append(1)
    count = 0
    for follower in followers_tweets:
        if os.path.isfile(followers_file_path + follower) == False:
            continue
        print "check follower %s, %d left" % (follower,userNumber - count)
        with open(followers_file_path + follower) as f:
            # lines = f.readlines()
            text = f.read()
            id = 0
            for candidate in usercandidate:
                # for line in lines:
                try:
                    # if text.find(candidate[0]):
                    if re.search(" " + candidate[0] + "[^\w]?",text) != None:
                        tfidf[id] += 1
                        break
                except Exception as e:
                    pass
                id += 1
        count += 1
    id = 0
    for uc in usercandidate:
        value = math.log(userNumber * 1.0 / tfidf[id]) * uc[1]
        tfidf[id] = value
        id += 1
    # tfidf = map(lambda value:math.log(value * 1.0 / userNumber) * usercandidate[key],tfidf)
    return tfidf

'''
步骤5:计算TextRank-TFIDF排序
'''
def CalucateSum(matrix):
    op = []
    for i in range(matrix.shape[0]):
        sum = 0
        for j in range(matrix.shape[0]):
            sum += matrix[i,j]
        op.append(sum)
    return op

def CalculateWeight(usercandidate):
    matrix = []
    for u1 in range(len(usercandidate)):
        line = []
        for u2 in range(len(usercandidate)):
            weight = min(usercandidate[u1][1],usercandidate[u2][1])
            line.append(weight)
        matrix.append(line)
    oldmatrix = mat(matrix)
    newmatrix = []
    op = CalucateSum(oldmatrix)
    # print op
    for i in range(oldmatrix.shape[0]):
        line = []
        for j in range(oldmatrix.shape[0]):
            line.append(float(oldmatrix[i,j] * 1.0 / op[j]))
        newmatrix.append(line)
    newmatrix = mat(newmatrix)
    return newmatrix

def CalculateTextRank(ucMatrix,threshold,dampFactor,idf,InitTRMatrix):
    TFIDFMatrix = mat(idf).T * (1 - dampFactor) / BeatFactor
    # print TFIDFMatrix
    TRMatrix = InitTRMatrix.T
    oldMatrix = TRMatrix
    # iteration
    iteration = 0
    while True:
        newMatrix = TRMatrix = ucMatrix * TRMatrix + TFIDFMatrix
        # newMatrix = TRMatrix = ucMatrix * TRMatrix

        flag = True
        for i in range(newMatrix.shape[0]):
            if math.fabs(newMatrix[i,0] - oldMatrix[i,0]) > threshold:
                flag = False
                break
        if flag == True:
            break
        iteration += 1
        if iteration == 20000:
            break
        # print iteration
        oldMatrix = TRMatrix
    print "the number of iteration is %d " % iteration
    return TRMatrix

def CalucateUCTR(usercandidate,ucTRMatrix):
    ucTR = {}
    i = 0
    for user in usercandidate:
        candidate = user[0]
        TR = ucTRMatrix[i,0]
        i += 1
        ucTR[candidate] = TR
    # 按照ucTR的键值排序
    ucTR = sorted(ucTR.items(),key = lambda dic:dic[1],reverse = True)
    print ucTR[:10]
    ucTR10,ucTR50 = ucTR[:10],ucTR[:50]
    return ucTR10,ucTR50

def ProcessBio(user_name):
    pass

def GenerateTargetUserInterest(Target_name,path,followers_path):
    # 初始矩阵设为权值都为1的矩阵
    TR = [1 for i in range(50)]
    InitTRMatrix = mat(TR)

    target_user_name = Target_name
    steponetime = time.time()
    target_user_candidate = getUserTopInterest(path,target_user_name)
    steptwotime = time.time()
    print "第一步计算用户兴趣候选集,用时 %f s" % (steptwotime - steponetime)
    print "正在计算TFIDF,大约需要几分钟"
    idf = CalculateTFIDF(target_user_candidate,followers_path)
    print "第二步计算用户TFIDF特征,用时 %f s" % (time.time() - steptwotime)
    print "开始TextRank迭代计算用户兴趣候选集排序,计算中"
    trstarttime = time.time()
    uiMatrix = CalculateWeight(target_user_candidate)
    ucTRMatrix = CalculateTextRank(uiMatrix,0.0001,0.85,idf,InitTRMatrix)
    Interest10,Interest50 = CalucateUCTR(target_user_candidate,ucTRMatrix)
    trendtime = time.time()
    print "迭代过程耗时 %f s" % (trendtime - trstarttime)
    return Interest10,Interest50

# 测试标签云库，将用户兴趣集可视化
def GenerateTagCloud(InterestSorted,name):
    newdic = []
    for d in InterestSorted:
        newdic.append((d[0],d[1] * 10000))
    tags = make_tags(newdic, minsize = 5,maxsize=30)
    # 保存在当前目录下
    create_tag_image(tags, name + 'tags.png', size=(700, 600), fontname='Nobile')
    webbrowser.open(name + 'tags.png') # see results


# 对外接口,返回该用户前10个兴趣标签
def GenerateInterestsWithFollowers(screen_name,path=target_tweets_path,followers_path=followers_file_path):
    '''
    :param path: 该用户推文路径
    :param screen_name: 该用户screen_name
    :param followers_path: 该用户粉丝们的推文路径
    :return:
    '''
    Interest10,Interest50 = GenerateTargetUserInterest(screen_name,path,followers_path)
    # 将50个兴趣标签生成TagCloud
    GenerateTagCloud(Interest50,screen_name)
    return Interest10

# 对外接口,返回该用户前10个兴趣标签,但不在粉丝中TextRank排序
def GenerateInterestsWithTF(screen_name,path=target_tweets_path):
    '''
    :param path: 该用户推文路径
    :param screen_name: 该用户screen_name
    :param followers_path: 该用户粉丝们的推文路径
    :return:
    '''
    Interest10 = getUserTopInterest(path,screen_name)[:10]
    return Interest10





