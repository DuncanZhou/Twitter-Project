#!/usr/bin/python
#-*-coding:utf-8-*-
'''@author:duncan'''

# 与Msql交互层
import MySQLdb
import MySQLdb.cursors
import config
import sys
sys.path.append("..")
from TwitterUsers import TwitterUsers


# 数据库连接
def Connection():
    conn = MySQLdb.connect(
        host=config.host,
        port = config.port,
        user=config.user,
        passwd=config.passwd,
        db =config.db,
        # 以字典形式返回结果
        cursorclass = MySQLdb.cursors.DictCursor,
    )
    # 全局变量cursor
    cursor = conn.cursor()
    return conn,cursor

# 数据库关闭
def Close(conn,cursor):
    cursor.close()
    conn.commit()
    conn.close()

# 根据用户id查询用户信息
def getUserInfo(id,table):
    '''
    :param id: 用户id
    :param table: 表名
    :param cursor: cursor
    :return:
    '''
    conn,cursor = Connection()
    cursor.execute("SELECT * FROM %s where userid = '%s'" % (table,id))
    data = cursor.fetchall()
    twitter_user = TwitterUsers.User(data[0]['userid'],data[0]['screen_name'],data[0]['name'],data[0]['location'],data[0]['statuses_count'],data[0]['friends_count'],data[0]['followers_count'],data[0]['favourites_count'],data[0]['verified'],data[0]['category'],data[0]['influenceScore'],data[0]['rank_influ'])
    Close(conn,cursor)
    return twitter_user

# 获取表内所有用户的信息
def getUsersInfo(table):
    # db = Conn(hostname,username,password,databasename)
    # cursor = db.cursor()
    conn,cursor = Connection()
    cursor.execute("SELECT * FROM %s" % table)
    data = cursor.fetchall()
    user = []
    for d in data:
        twitter_user = TwitterUsers.User(d['userid'],d['screen_name'],d['name'],d['location'],d['statuses_count'],d['friends_count'],d['followers_count'],d['favourites_count'],d['verified'],d['category'],d['influenceScore'],d['rank_influ'])
        user.append(twitter_user)
    Close(conn,cursor)
    return user

# 获取某一类别的用户
def getUsersByCategory(table,category):
    conn,cursor = Connection()
    users = []
    cursor.execute("select * from '%s' where category = '%s'" % (table,category))
    data = cursor.fetchall()
    for d in data:
        twitter_user = TwitterUsers.User(d['userid'],d['screen_name'],d['name'],d['location'],d['statuses_count'],d['friends_count'],d['followers_count'],d['favourites_count'],d['verified'],d['category'],d['influenceScore'],d['rank_influ'])
        users.append(twitter_user)
    Close(conn,cursor)
    return users

# 更新影响力分数
def updateUserInfluScore(table,userid,influscore):
    conn,cursor = Connection()
    sql = "update %s set influenceScore = %f where userid = '%s'" % (table,influscore,userid)
    cursor.execute(sql)
    Close(conn,cursor)

def updateUserInfluRank(table,userid,rank_influ):
    conn,cursor = Connection()
    sql = "update %s set rank_influ = %d where userid = '%s'" % (table,rank_influ,userid)
    cursor.execute(sql)
    Close(conn,cursor)

# 获取分类和分类人数
def getCategories(table):
    categories = []
    number = []
    conn,cursor = Connection()
    sql = "select category,count(*) as number from %s group by category" % table
    cursor.execute(sql)
    data = cursor.fetchall()
    for d in data:
        categories.append(d['category'])
        number.append(d['number'])
    Close(conn,cursor)
    return categories,number

# 更新用户的心理状态
def updateUserPsy(table,userid,psy):
    conn,cursor = Connection()
    sql = "update %s set psy = %d where userid = '%s'" % (table,psy,userid)
    cursor.execute(sql)
    Close(conn,cursor)