#!/usr/bin/python
#-*-coding:utf-8-*-
'''@author:duncan'''


import sys
sys.path.append("..")
from Neo4jInteraction import TwitterWithNeo4j as neo4j
relationships_path = "relationships"

# 创建结点
def CreateNodes(path):
    '''

    :param path: CSV文件路径
    :return:
    '''
    neo4j.CreateNodesFromCSV(path)

# 初始化操作
def Initial(path="file:///users.csv"):
    '''
    :param path: csv路径
    :return:
    '''
    # csv文件需要放在默认import目录下
    CreateNodes(path)

    # 建立索引
    neo4j.IndexBySName()

    # 设置userid为唯一
    neo4j.UniqueID()

# 从文件中批量插入用户之间关系
def InsertUsersRels(path):
    with open(path,'r') as f:
        lines = f.readlines()
    count = 0
    for line in lines:
        names = line.split("\t")
        # 对文件末尾去除\r\n
        neo4j.InsertRel(names[0],names[1].replace("\r\n",""))
        count += 1
        print "已插入%d条人物关系" % count

# 查询两个用户是否有follows关系
def isFollow(sname1,sname2):
    return neo4j.isFollow(sname1,sname2)

# 单条插入关系
def InsertRel(sname1,sname2):
    neo4j.InsertRel(sname1,sname2)

# 查询某用户的关联用户,深度不小于7(默认参数=1)
def SearchFollowersByDepth(sname):
    users = neo4j.SearchFollowersByDepth(sname)
    return users

# 查询某个领域内的用户
def SearchUsersByCategory(sname):
    users = neo4j.SearchUsersByCategory(sname)
    return users

if __name__ == '__main__':
    # 初始化操作,最开始执行一次
    # Initial()
    pass
