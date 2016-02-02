#!/usr/bin/env python
#coding: utf-8
import codecs, sys, re, MeCab, numpy, os

import numpy as np
import matplotlib.pyplot as plt
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stdin = codecs.getreader('utf-8')(sys.stdin)

dict = {}
dict_list = []

#textを形態素解析して、名詞のみのリストを返す
def extractKeyword(text):
    tagger = MeCab.Tagger('-Ochasen')
    node = tagger.parseToNode(text)
    keywords = []
    while node:
        if node.feature.split(",")[0] == u"名詞":
            if node.feature.split(",")[1] not in [u"サ変接続",u"数"]: #記号と数は省く
                keywords.append(node.surface)
        node = node.next
    return keywords

#stringから名詞のみを抽出し、dictに出現回数をカウントする
def count_nom(string):
    keywords = extractKeyword(string)
    for x in keywords:
        if x in dict:
            dict[x]+= 1
        else:
            dict[x] = 1

#保存先のフォルダ及びファイルの確認
try:
    files = os.listdir('./freq')
except OSError:
    os.makedirs('./freq')#フォルダがなければ作る

#フォルダごとに名詞を集計
dirs = os.listdir('data/livedoor_news')
dirs.sort()
j=0
for directory in dirs:
    #フォルダ内のファイルすべてをリストに格納
    files = os.listdir('data/livedoor_news/%s'%directory)
    files.sort()

    #ファイル毎に名詞を数える
    dict={}
    for file in files:
        print file
        k = "data/livedoor_news/%s/%s"%(directory, file)  
        f = codecs.open("%s"%k,"r","utf-8")
        string = f.read().encode("utf-8","replace")
        f.close()
    
        count_nom(string)
        
    #集計結果を出力(フォルダ毎)
    f = open('freq/freq_%d.txt'%j, 'w')
    total_nom = 0
    for k, v in sorted(dict.items(), key=lambda x:x[1], reverse = True):
        total_nom += v
    f.write("total\t%d\tnominals"%total_nom + "\n\n")
    for k, v in sorted(dict.items(), key=lambda x:x[1], reverse = True):
        f.write(str(u"%s\t%d" %(k,v) ) + "\n")  
    f.close()
    j+=1
    dict_list.append(dict)#トータル用にフォルダ毎の集計を保持
    

#トータルの集計をとる
total_nom = 0
total_dict = {}
for i in range(len(dict_list)): 
    for k, v in sorted(dict_list[i].items(), key=lambda x:x[1], reverse = True):
        total_nom += v
        if k in total_dict:
            total_dict[k] += v
        else:
            total_dict[k] = v

#集計結果を出力(トータル)
f = open('freq/freq_total.txt', 'w')
f.write("total %d nominals"%total_nom + "\n\n")  
for k, v in sorted(total_dict.items(), key=lambda x:x[1], reverse = True):
    f.write(str(u"%s\t%d" %(k,v) ) + "\n")  
f.close()
