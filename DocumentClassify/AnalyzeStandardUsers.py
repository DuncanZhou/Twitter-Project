#!/usr/bin/python
#-*-coding:utf-8-*-
'''@author:duncan'''

import re
import time
import sys
sys.path.append("..")
from MySQLInteraction import TwitterWithMysql as mysql
from MongoDBInteraction import TweetsWithMongo as mongo
import config
import TweetsClassify
from nltk.corpus import stopwords
from nltk import word_tokenize
import pickle

project_folder_path = config.project_folder_path

# # 导入另一个文件夹下的脚本
# from sys import path
# path.append(project_folder_path + "/TwitterProject/TwitterUsers/")
# import TwitterUsers

# hostname = "localhost"
# username = "root"
# password = "123"
# databasename = "TwitterUserInfo"


stopwords = config.stopwords
Classifiers = [config.mnb,config.svm,config.forest,config.sgd,config.etree]

# 并不是把推文全部作为输入,在去除推文中停用词并将所有单词作为输入
def GetClassifyResultsByWords(users_id,collection_name="tweets"):
    # 四种分类器的权值
    weight = [0.4,0.3,0.1,0.1,0.1]
    results = []
    multiclassifier_result = {}
    MultinomialNB_resdic = {}
    # LinearSVM_resdic = {}
    # RandomForest_resdic = {}
    # SGD_resdic = {}
    # ExtraTree_resdic = {}

    count = 0
    for id in users_id:
        # 获取用户推文
        text = mongo.getUserTweets(id,collection_name)
        # 删除推文中@的人
        re.sub(r"""\n@.+"""," ",text)
        # words = word_tokenize(text.decode("utf-8"))
        words = word_tokenize(text)
        # 判断是否是单词,去除停用词
        wordlist = [word for word in words if word.isalpha() and word.lower() not in stopwords]

        # 以下步骤统计词频,由于统计词频效果不好,故舍弃
        # wordset = set(wordlist)
        # worddic = {}
        # for word in wordset:
        #     worddic[word] = wordlist.count(word)
        # worddic = sorted(worddic.items(),key=lambda dic:dic[1],reverse=True)
        # lastwords = [word[0] for word in worddic[:4000]]

        # 合并成文本
        # text = " ".join(lastwords)
        text = " ".join(wordlist)
        # 单模型
        MultinomialNB_res = TweetsClassify.Classify(text,config.mnb)
    #     LinearSVM_res = TweetsClassify.Classify(text,"LinearSVM")
    #     RandomForest_res = TweetsClassify.Classify(text,"RandomForest")
    #     SGD_res = TweetsClassify.Classify(text,"SGD")
    #     ExtraTree_res = TweetsClassify.Classify(text,"ExtraTree")
    #
        MultinomialNB_resdic[id] = MultinomialNB_res
    #     LinearSVM_resdic[id] = LinearSVM_res
    #     RandomForest_resdic[id] = RandomForest_res
    #     SGD_resdic[id] = SGD_res
    #     ExtraTree_resdic[id] = ExtraTree_res
    # results.append(MultinomialNB_resdic)
    # results.append(LinearSVM_resdic)
    # results.append(RandomForest_resdic)
    # results.append(SGD_resdic)
    # results.append(ExtraTree_resdic)

        # 多模型融合
        result = TweetsClassify.Classify_MultiModels(text,Classifiers,weight)
        multiclassifier_result[id] = result
        count += 1
        print "finished %d users" % count
    return multiclassifier_result,MultinomialNB_resdic

# 从mysql中查询用户的分类形成字典返回
def GetCategoryById(users):
    category_dic = {}
    for user in users:
        category_dic[user.id] = user.category
    return category_dic

# 在结果中计算某一类别的人数
def calcCategoryN(results,category):
    number = 0
    for key in results.keys():
        if results[key] == category:
            number += 1
    return number

# 在结果中计算某一类别中正确的个数
def calcCategoryCorrectN(results,category,ground_truth):
    number = 0
    for key in results:
        if results[key] == category and results[key] == ground_truth[key]:
            number += 1
    return number

# 计算每个领域的准确率和召回率
def Accuracy(table="StandardUsers"):
    StandardUsers = mysql.getUsersInfo(table)
    categories = mysql.getCategoriesAndNumber(table)

    # 将用户的id保存
    StandardUsers_id = []

    for user in StandardUsers:
        StandardUsers_id.append(user.id)
    # ground_truth
    category_dic = GetCategoryById(StandardUsers)

    # 采用预处理后的推文作为输入
    MultiModels_results,Multinomial_results = GetClassifyResultsByWords(StandardUsers_id)
    save_file = open("results.pickle","wb")
    pickle.dump(Multinomial_results,save_file)
    save_file.close()

    categories_sprecision = {}
    categories_mprecision = {}
    categories_srecall = {}
    categories_mrecall = {}
    for category in categories.keys():
        # 计算在结果中共有多少该类别
        number_in_mclassify = calcCategoryN(MultiModels_results,category)
        number_in_sclassify = calcCategoryN(Multinomial_results,category)

        # 计算在结果中该类别中有多少正确的
        correct_number_in_sclassify = calcCategoryCorrectN(Multinomial_results,category,category_dic)
        correct_number_in_mclassify = calcCategoryCorrectN(MultiModels_results,category,category_dic)

        # 准确率
        categories_sprecision[category] = correct_number_in_sclassify * 1.0 / number_in_sclassify
        categories_mprecision[category] = correct_number_in_mclassify * 1.0 / number_in_mclassify

        # 召回率
        categories_srecall[category] = correct_number_in_sclassify * 1.0 / calcCategoryN(category_dic,category)
        categories_mrecall[category] = correct_number_in_mclassify * 1.0 / calcCategoryN(category_dic,category)

        print "单模型 %s: 准确率 %f, 召回率 %f" % (category,categories_sprecision[category],categories_srecall[category])

if __name__ == '__main__':

    start = time.time()
    Accuracy()
#     # 获取标准人物样本库中的用户
#     StandardUsers = mysql.getUsersInfo('StandardUsers')
#
#     # 将用户的id保存
#     StandardUsers_id = []
#     # i = 0
#     for user in StandardUsers:
#         StandardUsers_id.append(user.id)
#
# #------------------------------------------------选择训练集训练--------------------------------
#     '''
#     BCC分类：business/entertainment/politics/sport/technology
#     CNN分类：agriculture/economy/education/entertainment/military/politics/religion/sports/technology
#
#     DataSet1 是 CNN + BCC新闻数据集(分类融合起来)
#     DataSet2 是 BCC新闻数据集(加了维基词条的一些文章,加了CNN的一些文本,结果有提升)
#     DataSet3 是 CNN新闻数据集
#     DataSet4 是 CNN + BCC新闻数据集(CNN填补BCC没有的分类)
#     DataSet5 是 CNN新闻 + BCC新闻 + 推文数据集(融合)
#     '''
#
#     print "----------------------------开始分类------------------------------------------------"
#     # ground_truth
#     category_dic = GetCategoryById(StandardUsers)
#
#     # 采用预处理后的推文作为输入
#     MultiModels_results,Multinomial_results = GetClassifyResultsByWords(StandardUsers_id)
#
#     # 将多项式分类器分类结果写入文件
#     with open("/home/duncan/Multinomial_NB_Classifier-results",'w') as f:
#         for key in Multinomial_results.keys():
#             for user in StandardUsers:
#                 if user.id == key:
#                     f.write(user.id + "  ==>  " + "分类器分类结果: " + Multinomial_results[key] + "  ==>  " + "正确结果: " + user.category)
#                     f.write("\n")
#                     break
#     accuracy = TweetsClassify.Accuracy(Multinomial_results,category_dic)
#     print "分类结果:多项式贝叶斯分类器:共%d个名人,分类准确率为%f" % (len(Multinomial_results),accuracy)
#
#     # 多分类器融合结果写入文件
#     with open("/home/duncan/MultiClassifier-results",'w') as f:
#         for key in MultiModels_results.keys():
#             for user in StandardUsers:
#                 if user.id == key:
#                     f.write(user.id + "  ==>  " + "分类器分类结果: " + MultiModels_results[key] + "  ==>  " + "正确结果: " + user.category)
#                     f.write("\n")
#                     break
#     accuracy = TweetsClassify.Accuracy(MultiModels_results,category_dic)
#     print "分类结果:分类器融合:共%d个人物,分类准确率为%f" % (len(MultiModels_results),accuracy)
#     print "-------------------------------------------------------------------------------------------"

    end = time.time()
    print "共用时%fs" % (end - start)
