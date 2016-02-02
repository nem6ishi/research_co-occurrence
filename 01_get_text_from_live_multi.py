#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 保存先のフォルダの関係上、十万以上の位は揃える。
gsnum = 9400000#始点
genum = 9410000#終点

import os, urllib2, re, codecs, sys, time, httplib
from multiprocessing import Process

#dataのエンコードを返す
def conv_encoding(data):
    lookup = ('utf_8', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213',
              'shift_jis', 'shift_jis_2004','shift_jisx0213',
              'iso2022jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_3',
              'iso2022_jp_ext','latin_1', 'ascii')
    encode = None
    for encoding in lookup:
        try:
            data = data.decode(encoding)
            encode = encoding
            break
        except:
            pass
    if isinstance(data, unicode):
        return encode
    else:
        raise LookupError


#urlからテキスト抽出、のち保存
def get_text(raw, url_num):
    #html形式でデータ抽出
    htmlfp = raw
    en = htmlfp.read()
    encode = conv_encoding(en)
    html = en.decode(encode, "replace")
    htmlfp.close()
    
    #html形式のデータを一行または一文ごとにリストに格納
    h = html.encode("utf-8")
    h = re.sub(r'。」',"」",h)
    lst = re.split("。|\n", h)
    
    flag = 0
    st="\n"

    #本文のみstに取り出す
    for l in lst:
        if "articleBody" in l: #livedoor_newsではこれで本文が見つかる
            flag = 1  
        if flag==1:
            st += l.strip()
            st += "。\n"
        if "/span" in l:
            flag = 0   

    #余分なものを取り除く
    st = re.sub(r'<(\"[^\"]*\"|\'[^\']*\'|[^\'\">])*>',"",st) #htmlのタグを除去
    st = re.sub(r'\n。',"",st)
    st = re.sub(r'　',"",st).strip()
    
    #stをファイルに保存
    folder = int(int(url_num)/10000)*10000
    f = open('data/livedoor_news/news%s-/news%s.txt'%(str(folder),str(url_num)), 'w')
    f.write(st.strip())
    f.close()


#記事番号snum番からblock個ずつ飛ばして記事の保存
def get_article(snum, block):
    global files, genum
    for i in range(10000/block):
        j = snum + (i*block)
        tmp = str(j)
        if j > genum:#終点判定
            break
        if "news%s.txt"%tmp in files:#既に取得済みであればパス
            print "pass %i"%j
            continue

        k = "http://news.livedoor.com/article/detail/%s/"%tmp
    
        #urlが存在するか確認
        try:
            htmlfp = urllib2.urlopen(k)
        except (IOError, httplib.HTTPException):#urlがみつからなくてもパス
            print "not exist", tmp
            continue
        
        print "\n ",tmp, "\n  this page exists\n"  
        get_text(htmlfp, tmp)#urlがみつかったので保存作業をする



#メインプログラム
if __name__ == '__main__':
    start = time.time()

    snum_article = gsnum
    snum0=int(snum_article/10000)*10000
    enum_article = genum
    print snum_article,"to",str(int(enum_article)-1)

    #保存先のフォルダ及びファイルの確認
    try:
        files = os.listdir('data/livedoor_news/news%s-'%snum0)
    except OSError:
        os.makedirs('data/livedoor_news/news%s-'%snum0)#フォルダがなければ作る
        files = os.listdir('data/livedoor_news/news%s-'%snum0)

    #multiprocessingで並列処理。block個に処理を分け、分けた個数分jobsを作る。
    job_nlist=[]
    block = 10
    for i in range(block):
        job_nlist.append(i)
    #jobとしてget_articleを入れる。引数は最初の記事番号と何個飛ばしかの数。
    jobs=[]
    for i in job_nlist:
        j = snum0 + int(i)
        jobs.append( Process(target=get_article, args=(j,block) ) )

    #並列処理の実行
    for j in jobs:
        j.start()
    for j in jobs:
        j.join()


    #経過時間の表示
    elapsed_time = time.time() - start
    print "\nelapsed time : ", elapsed_time
    print "%f"%(elapsed_time/(enum_article-snum_article)),"(per one article)\n"
