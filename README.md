# research_co-occurrence 
livedoor_newsの文章を取り出し、それについて名詞の出現率、共起頻度を調査。  

### 01_get_text_from_live_multi.py livedoor_newsの文章を抜き取り、保存する。  

urlを開くのに時間がかかるのでマルチスレッド化。  

それでも遅い。   

### 02_live_freq.py 

単語の出現回数を調査。  

### 03_one_to_some_relation.py 

一つの単語に対して、共起(同一文中)する単語の調査。  

### 04_two_deep_rlivedoor.py  

二つの単語に対して、共起(同一文中)する単語の調査。
