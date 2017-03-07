#!/usr/bin/python
#-*-coding:utf-8-*-
'''@author:duncan'''

import os
import re
import nltk
import math
import time
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from numpy import *

BeatFactor = 300000

project_path = os.path.abspath("..")
project_folder_path = os.path.abspath(".." + os.path.sep + "..")
twitter_stop_words = ["@","from","TO","to",":","!",".","#","https","RT","URL","in","&",";","re","''","?","thank","thanks","do","be","today","yesterday","tomorrow","night","tonight","day","year","last","oh","yeah"]
followers_file_path = project_folder_path + "/TweetsSamples/"
target_tweets_path = project_folder_path + "/TweetsSamples/"

# usercandidate = []

def PreProcess(text):
    # open_file = open(slang_file_path,"rb")
    # slang = pickle.load(open_file)
    # open_file.close()

    # clear @/#/http
    toClear = re.findall(r'[@|#][\d|\w|_]+|http[\w|:|.|/|\d]+',text)
    # print toClear
    for c in toClear:
        text = text.replace(c," ")
    # print text
    wordslist = []
    if text == "" or text == None:
        return []
    words = word_tokenize(text)
    # clear @/#/url/emotion
    for word in words:
        # count = 0
        if word not in (stopwords.words("english") and twitter_stop_words):
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
        if len(word) != 0 and word not in (stopwords.words("english") and twitter_stop_words) and len(word) <= 20:
            usercandidate.append(word.lower())
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
单用户使用TF词频排序,并生成前100兴趣候选集
'''
def CalculateTF(usercandidate):
    vac = set(usercandidate)
    vacdic = {}
    for phase in vac:
        vacdic[phase] = usercandidate.count(phase)
    # 按照键值排序
    vacdic = sorted(vacdic.items(),key = lambda dic:dic[1],reverse = True)
    # 输出前100个兴趣候选集
    return vacdic[:100]

def getUserTop100Interest(path,screen_name):
    # global usercandidate
    usercandidate = []
    with open(path + screen_name,"r") as f:
        lines = f.readlines()
        for line in lines:
            # 移除回复/对话的推文 （是以@XXXX开头）
            if re.match(r"^@[\w|_]+",line) == None:
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
    tfidf = {}
    count = 0
    for follower in followers_tweets:
        print "check follower %s, %d left" % (follower,userNumber - count)
        with open(followers_file_path + follower) as f:
            lines = f.readlines()
            for candidate in usercandidate:
                for line in lines:
                    try:
                        if line.find(candidate[0]):
                            tfidf[candidate[0]] += 1
                            break
                    except Exception as e:
                        continue
        count += 1
    for key in tfidf.keys():
        tfidf[key] = math.log(tfidf[key] * 1.0 / userNumber) * usercandidate[key]
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
    TFIDFMatrix = mat(idf) * (1 - dampFactor) / BeatFactor
    TRMatrix = InitTRMatrix.T
    oldMatrix = TRMatrix
    # iteration
    iteration = 0
    while True:
        newMatrix = TRMatrix = ucMatrix * TRMatrix + TFIDFMatrix.T
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

if __name__ == "__main__":
    target_user_name = "realDonaldTrump"
    steponetime = time.time()
    target_user_candidate = getUserTop100Interest(target_tweets_path,target_user_name)
    steptwotime = time.time()
    print "first step uses %f seconds" % (steptwotime - steponetime)
    CalculateTFIDF(target_user_candidate,followers_file_path)
    print "seconde step uses %f seconds" % (time.time() - steptwotime)



