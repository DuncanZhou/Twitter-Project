#!/usr/bin/python
#-*-coding:utf-8-*-
'''@author:duncan'''


import sys
sys.path.append("..")
from Neo4jInteraction import TwitterWithNeo4j as neo4j

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

if __name__ == '__main__':
    # Initial()
    # 查询两个用户是否有follows关系
    # print neo4j.isFollow("22mosalah","realDonaldTrump")
    neo4j.InsertRel("22mosalah","realDonaldTrump")
