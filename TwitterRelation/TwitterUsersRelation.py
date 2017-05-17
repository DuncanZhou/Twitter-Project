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

# 从文件中插入用户之间关系
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

if __name__ == '__main__':
    # 初始化操作,最开始执行一次
    # Initial()

    # 查询两个用户是否有follows关系
    # print neo4j.isFollow("22mosalah","realDonaldTrump")

    # 单条插入关系
    # neo4j.InsertRel("22mosalah","realDonaldTrump")

    # 从文件中批量插入关系
    InsertUsersRels(relationships_path)

    # 查询某用户的关联用户,深度不小于7

