#!/usr/bin/env python
#coding: utf-8
import codecs, sys, re, MeCab, os

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stdin = codecs.getreader('utf-8')(sys.stdin)


#textを形態素解析して、名詞のみのリストを返す
def extractKeyword(text):
    tagger = MeCab.Tagger('-Ochasen')
    node = tagger.parseToNode(text)
    keywords = []
    while node:
        if node.feature.split(",")[0] == u"名詞":
            if node.feature.split(",")[1] not in [u"サ変接続",u"数"]:
                keywords.append(node.surface)
        node = node.next
    return keywords


#一記事分であるstringと数える名詞のリストsearch_wordsをもとに共起回数をカウント
def count_rel(string, search_words):
    global sen_lst
    global rel_dict_list

    #stringを一文ごとにリストに格納
    lst = []
    string = re.sub(r'。」','」', string)
    lst = re.split("？|！|。|\n|\t", string)

    #一文ごとにsearch_words内の名詞があるか調べて共起名詞を格納
    for sent in lst:
        sent = sent.strip()
        keywords = extractKeyword(sent) #keywords : list only nominals
        i = 0
        
        #処理は一文に対して、search_words内の名詞一つ一つを照らし合わせる
        for search_word in search_words:
            rel_dict_list[i][0] = search_word#共起頻度を調べる名詞を入れておく
#文にsearch_wordがあればカウントに移る
            if search_word[0] in keywords and search_word[1] in keywords:
                for x in keywords:
                    if x in search_word:#調べる名詞自体はカウントしない
                        continue
                    #他の名詞は漏らさずカウント
                    if x in rel_dict_list[i][1]:
                        rel_dict_list[i][1][x] += 1
                    else:
                        rel_dict_list[i][1][x] = 1
            i += 1

#調べたい名詞ペアをsearch_wordsに格納
search_words=[]
search_words.append(["日本","市場"])
search_words.append(["日本","世界"])
search_words.append(["日本","中国"])
search_words.append(["日本","株式会社"])
search_words.append(["日本","jp"])
search_words.append(["日本","韓国"])
search_words.append(["日本","戦"])
search_words.append(["日本","国内"])
search_words.append(["日本","www"])
search_words.append(["日本","国"])
search_words.append(["日本","経済"])
search_words.append(["日本","シリーズ"])
search_words.append(["日本","協会"])
search_words.append(["日本","アジア"])
search_words.append(["日本","米"])


#調べる名詞の数の分、共起頻度を格納するリストを作る
rel_dict_list = []
for i in range(len(search_words)):
    rel_dict_list.append(["null",{}])#形式は[調べる名詞達のlist,共起頻度のdict]


#参照する10個のフォルダの名前を取っておく
dirs = os.listdir('data/livedoor_news')
dirs.sort()

#フォルダごとに処理をかける
for directory in dirs:
    files = os.listdir('data/livedoor_news/%s'%directory)
    files.sort()
    #ファイル(記事)ごとに共起頻度を数える
    for file in files:
        print file
        k = "data/livedoor_news/%s/%s"%(directory,file)  
        f = codecs.open("%s"%k,"r","utf-8")
        string = f.read().encode("utf-8","replace")
        f.close()

        #stringとsearch_wordsを渡して、カウントする関数に任せる
        count_rel(string, search_words)
  

#全名詞の頻度をdictに取り込んでおく
k = "freq/freq_total.txt"  
f = codecs.open("%s"%k,"r","utf-8")
string = f.read().encode("utf-8","replace")
f.close()

i = 0
dict = {}
data_list = re.split("\n", string)
for s in data_list:
    i += 1
    if i < 3 or len(s) < 2:
        continue
    lst = re.split("\t", s)
    dict[lst[0]] = int(lst[1])
all_total = 0
for k, v in dict.items():
        all_total += v


#結果を出力(調べた名詞ごとに出力)
for i in range(len(rel_dict_list)):
    total = 0
    for k, v in rel_dict_list[i][1].items():
        total += v

    f = open('rel/text-relation_%s_%s.txt'\
                 %(rel_dict_list[i][0][0],rel_dict_list[i][0][1]), 'w')
    f.write("total : %d"%total + "\n\n")  
    for k, v in sorted(rel_dict_list[i][1].items(),\
                           key=lambda x:x[1], reverse = True):
       #出現回数、割合、全名詞での出現割合を出力
        if k not in dict:
            print "%s is not in dict"%k
            continue
        #if  (float(v)/total)/(dict[k]/float(all_total)) >= 2.0 :#２倍のものに限る処理
            f.write(str(u"%s\t\t%d\t\t%f\t\t%f"\
                            %(k, v, float(v)/total, dict[k]/float(all_total))) + "\n")
    f.close()
