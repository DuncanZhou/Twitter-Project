#!/usr/bin/python
#-*-coding:utf-8-*-
'''@author:duncan'''

import os
import pickle

project_folder_path = os.path.abspath(".." + os.path.sep + "..")
following_path = project_folder_path + "/following/"
follower_path = project_folder_path + "/follower/"
following_dic_path = project_folder_path + "/FollowingDic/"
follower_dic_path = project_folder_path + "/FollowerDic/"

def getPrefix(path):
    prefix = os.listdir(path)
    prefix = map(lambda fname:fname.replace(".txt",""),prefix)
    return prefix

def getFileID(prefix,filepath):
    with open(filepath,"r") as f:
        suffix = []
        lines = f.readlines()
        lineid = 1
        for line in lines:
            if lineid % 2 != 0:
                line = line[1:].replace("\r\n","")
                suffix.append(line)
            lineid += 1
    userIDs = map(lambda line:prefix + line,suffix)
    return userIDs

def ConstructFollowingDic(path):
    dic = {}
    # 构造字典,对应每个文件中对应的id号
    filename = getPrefix(path)
    for file in filename:
        userID = set(getFileID(file,path + file + '.txt'))
        for uid in userID:
            dic[uid] = file
    # 将字典持久化
    save_file = open(following_dic_path + "followingdic.pickle","wb")
    pickle.dump(dic,save_file)
    save_file.close()
    return dic

def ConstructFollowerDic(path):
    dic = {}
    # 构造字典,对应每个文件中对应的id号
    filename = getPrefix(path)
    for file in filename:
        userID = set(getFileID(file,path + file + '.txt'))
        for uid in userID:
            dic[uid] = file
    # 将字典持久化
    save_file = open(follower_dic_path + "followerdic.pickle","wb")
    pickle.dump(dic,save_file)
    save_file.close()
    return dic

def getUserFollowing(uid,followingdic):
    path = following_path
    if uid not in followingdic:
        return []
    userfile = followingdic[uid]
    print "位于文件%s处" % userfile + '.txt'
    with open(path + userfile + ".txt","r") as f:
        lines = f.readlines()
    lineid = 0
    useridline = -1
    while lineid < len(lines):
        # print ":" + uid[len(userfile):]
        if lines[lineid].replace("\r\n","") == (":" + uid[len(userfile):]):
            useridline = lineid
            break
        else:
            lineid += 1
    if useridline != -1:
        following = lines[useridline + 1].replace("\r\n","")
    else:
        return []
    return following

def getUserFollower(uid,followerdic):
    path = follower_path
    if uid not in followerdic:
        return []
    userfile = followerdic[uid]
    # print "位于文件%s处" % userfile + '.txt'
    try:
        with open(path + userfile + ".txt","r") as f:
            lines = f.readlines()
    except Exception as e:
        return []
    lineid = 0
    useridline = -1
    while lineid < len(lines):
        # print ":" + uid[len(userfile):]
        if lines[lineid].replace("\r\n","") == (":" + uid[len(userfile):]):
            useridline = lineid
            break
        else:
            lineid += 1
    if useridline != -1:
        followers = lines[useridline + 1].replace("\r\n","")
    else:
        followers = lines[0].replace("\r\n","")
    return followers

def test():
    open_file = open(follower_dic_path + "followerdic.pickle","rb")
    follower_dic = pickle.load(open_file)
    open_file.close()
    print getUserFollower("1000",follower_dic)
# test()