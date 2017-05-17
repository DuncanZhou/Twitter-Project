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
    CREATE (:TwitterUser { name:line.userid,userid: line.userid, screen_name:line.screen_name,followers_count:line.followers_count,friends_count:toInt(line.friends_count),favourites_count:line.favourites_count,location:line.location,verified:toInt(line.verified),category:line.category})" % path
    # # 利用事务运行query
    with session.begin_transaction() as tx:
        tx.run(statement)
        tx.success = True
    # session.run(statement)
    Close(session,driver)

# 判断两个结点之间是否已经有follows关系
def isFollow(sname1,sname2):
    isFollow = False
    driver,session = Conn()
    statement = "MATCH (n:TwitterUser {screen_name:'%s'})-[:follows]->(m:TwitterUser {screen_name:'%s'}) RETURN exists((n)-[:follows]->(m)) as isFollow" % (sname1,sname2)
    result = session.run(statement)
    for res in result:
        isFollow = res['isFollow']
    Close(driver,session)
    return isFollow


# 装饰器函数,在插入两个结点之间的关系时先判断两个结点之间是否已经存在关系
def checkRel(func):
    def wrapper(sname1,sname2):
        driver,session = Conn()
        statement = "MATCH (n:TwitterUser {screen_name:'%s'})-[:follows]->(m:TwitterUser {screen_name:'%s'}) RETURN exists((n)-[:follows]->(m)) as isFollow" % (sname1,sname2)
        result = session.run(statement)
        for res in result:
            isFollow = res['isFollow']
        Close(driver,session)
        if(isFollow == True):
            print "关系已存在!"
        else:
            func(sname1,sname2)
    return wrapper

# 根据screen_name更新结点之间的关系
# 定义一个装饰器
@checkRel
def InsertRel(sname1,sname2):
    # id1用户followsid2用户
    # 增加这样的关系 (n:TwitterUser {screen_name:sname1})-[:follows]->(m:TwitterUser {screen_name:sname2})
    driver,session = Conn()
    statement = "MATCH (n:TwitterUser {screen_name:'%s'}),(m:TwitterUser {screen_name:'%s'}) CREATE (n)-[:follows]->(m)" % (sname1,sname2)
    # if(isFollow(sname1,sname2) == True):
    #     print "关系已存在!"
    #     return
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

# 查询到某一user深度为depth的follows关系
def SearchFollowersByDepth(sname,depth=1):
    followers = []
    '''

    :param sname: 目标用户的screen_name
    :param depth: 关系网深度,整型
    :return:
    '''
    driver,session = Conn()
    statement = "MATCH (followers:TwitterUser)-[:follows*..%d]->(targetUser:TwitterUser {screen_name:'%s'}) RETURN distinct followers.screen_name" % (depth,sname)
    # session运行带参
    results = session.run(statement)
    # 遍历结果集
    for record in results:
        followers.append(record['followers.screen_name'])
    Close(session,driver)
    return followers

# 查找某个领域的用户,返回screen_name
def SearchUsersByCategory(category):
    users = []
    driver,session = Conn()
    statement = "MATCH (user:TwitterUser {category:'%s'}) RETURN distinct user.screen_name" % (category)
    # session运行带参
    results = session.run(statement)
    # 遍历结果集
    for record in results:
        users.append(record['user.screen_name'])
    Close(session,driver)
    return users