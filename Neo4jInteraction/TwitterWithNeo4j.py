#!/usr/bin/python
#-*-coding:utf-8-*-
'''@author:duncan'''

# 该脚本为与neo4j交互层


from neo4j.v1 import GraphDatabase,basic_auth


def Conn():
    # 加载驱动
    # 加密方式
    driver = GraphDatabase.driver("bolt://localhost:7687",auth=basic_auth("neo4j","123"),encrypted=True)
    # 创建会话
    session = driver.session()
    return driver,session

def Close(session,driver):
    session.close()
    driver.close()

def CreateNodesFromCSV(path):
    '''
    :param path: CSV文件路径
    :return:
    '''
    driver,session = Conn()
    # 从CSV文件中创建结点
    statement = "LOAD CSV WITH HEADERS FROM '%s' AS line\
    CREATE (:TwitterUser { name:line.userid,userid: line.userid, screen_name:line.screen_name,followers_count:toInt(line.followers_count),friends_count:toInt(line.friends_count),favourites_count:line.favourites_count,location:line.location,verified:toInt(line.verified),category:line.category})" % path
    # # 利用事务运行query
    with session.begin_transaction() as tx:
        tx.run(statement)
        tx.success = True
    # session.run(statement)
    Close(session,driver)

# 根据screen_name更新结点之间的关系
def InsertRel(sname1,sname2):
    # id1用户followsid2用户
    # 增加这样的关系 (n:TwitterUser {screen_name:sname1})-[:follows]->(m:TwitterUser {screen_name:sname2})
    driver,session = Conn()
    statement = "MATCH (n:TwitterUser {screen_name:'%s'}),(m:TwitterUser {screen_name:'%s'}) CREATE (n)-[:follows]->(m)" % (sname1,sname2)
    with session.begin_transaction() as tx:
        tx.run(statement)
        tx.success = True
    Close(driver,session)

# 根据screen_name建立索引
def IndexBySName():
    driver,session = Conn()
    # 创建索引语句
    statement = "CREATE INDEX ON :TwitterUser(screen_name)"
    with session.begin_transaction() as tx:
        tx.run(statement)
        tx.success = True
    Close(session,driver)

# 增加约束条件
def UniqueID():
    driver,session = Conn()
    # 创建索引语句
    statement = "CREATE CONSTRAINT ON (user:TwitterUser) ASSERT user.userid IS UNIQUE"
    with session.begin_transaction() as tx:
        tx.run(statement)
        tx.success = True
    Close(session,driver)