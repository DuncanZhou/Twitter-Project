#!/usr/bin/python
#-*-coding:utf-8-*-
'''@author:duncan'''

import UserInfluNoPageRank as influ
from MySQLInteraction import TwitterWithMysql as mysql
import matplotlib.pyplot as plt


def getUserScore(userid,table):
    '''

    :param userid: 字符串形式的userid
    :return: 返回影响力分数
    '''
    score = influ.CalucateUserInfluence(userid,table)
    return score

def getUsersScore(table):
    users = mysql.getUsersInfo(table)
    count = 0
    for user in users:
        user.influenceScore = getUserScore(user.id,table)
        count += 1
        # 更新用户影响力分数
        mysql.updateUserInfluScore(table,user.id,user.influenceScore)
        print "完成计算%d用户" % count


def Conclusion():
    users1 = mysql.getUsersInfo("StandardUsers")
    users2 = mysql.getUsersInfo("twittercounter")
    influence = [0 for i in range(15)]
    for user in users1:
        influence[(int)(user.influenceScore) / 10] += 1
    for user in users2:
        influence[(int)(user.influenceScore) / 10] += 1
    labels = []
    for i in range(15):
        right = (i + 1) * 10
        left = i * 10
        labels.append((str(left) + '-' + str(right)))
    x = [i for i in range(15)]
    plt.figure(figsize=(20,10))
    plt.bar(x,influence,facecolor='lightskyblue',align="center",edgecolor="white",label="low")
    plt.bar(x[6:11],influence[6:11],facecolor='yellowgreen',align='center',edgecolor='white',label="medium")
    plt.bar(x[11:],influence[11:],facecolor='crimson',align='center',edgecolor='white',label="high")
    plt.legend(shadow=True)
    # 设置x轴标注
    plt.xticks(x,labels,rotation=30)
    # 加上柱形图上的y轴数据标注(b + 0.05表示在y值上方0.05处加上标注)
    for (a,b) in zip(x,influence):
        plt.text(a,b + 0.05,b,ha='center',va='bottom',fontsize=15)
    plt.title("7000 Twitter Users' Influence Score Distribution",fontsize=18)
    plt.xlabel("Influence Score",fontsize=15)
    plt.ylabel("the number of users",fontsize=15)
    # 连接中位数
    plt.plot(x,influence,'b--',color='#ff9999',linewidth=2)
    # plt.xlim(-0.5,len(labels) - 0.5)
    plt.show()
    return influence

print Conclusion()
# getUsersScore("StandardUsers")
# getUsersScore("StandardUsers")
# print getUserScore("129770778","twittercounter")
