#対象Webページからアルファベット情報をスクレイピングし、自動で送信


import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import numpy as np
import time
from selenium import webdriver
import pandas as pd
from collections import Counter

#辞書(Dataframe)を作成
def make_dictionary():
    global word_dictionary
    data = pd.read_csv('ejdic-hand-utf8.txt', sep="\t", header=None, error_bad_lines=False)
    word_list = []
    counter_list = []
    len_list = []
    for row in data.iloc[:,0]:
        # 複数意味を持つ単語の中に", "が含まれていれば分ける
        split_row = re.split(r'[, | |,|\(]', str(row))
        for word in split_row:
            # 余分な記号を持った単語は省く(複数の単語から成る単語などが多いから
            if re.search(r'[-|\0|\'|.|@]', word):
                continue
            else:
                # 丸がっこは省く
                modified_word = re.sub(r'[\)]','',word)
                # quは省いた記号の@で置換
                modified_counter_word = modified_word.lower().replace('qu','@')
                # リストにアペンド
                word_list.append(modified_word.lower())
                counter_list.append(Counter(modified_counter_word))
                len_list.append(len(modified_word))
    # DataFrameに格納
    word_dictionary = pd.DataFrame({'len':len_list, 'counter':counter_list, 'word_name':word_list})
    word_dictionary = word_dictionary.drop_duplicates(subset='word_name').reset_index(drop=True)
    return word_dictionary

# Beautiful Soupの情報からスクレイピングし、best_wordを探す
def scrape(soup : BeautifulSoup, stop_wordlist : list) -> list:
    word_text = ''
    best_word = ''
    one_point = []
    two_points = []
    three_points = []
    word_length = 16
    best_score = 0
    stop_count = 0
    #アルファベットの情報ひとつずつ取り出す
    for word in soup.find_all("td", valign="middle"):
#         print(word)
        word_1 = re.match(".*value\+='(.*?)'.*?",str(word)).group(1)
        point = re.match('.*class="letter (.*?)".*?',str(word)).group(1)
#         print(type(word_1))
        #それぞれのポイントリストにアルファベットを格納
        one_point.append(word_1.lower()) if point=='p1' else two_points.append(word_1.lower())  if point=='p2' else three_points.append(word_1.lower())
#         print(word_1) 
        word_text += word_1
    # 'Qu'だけはそれだけ
    word_counter = Counter(word_text.lower().replace('qu','@'))
    print(word_counter)
    # 3文字の単語の点数は高々100点なので4文字以上の単語のみ探索
    while(word_length > 3):
        # 4~16文字の長さの単語に絞る
        dictionary_1 = word_dictionary[word_dictionary['len']==word_length]
        for index, row in dictionary_1.iterrows():
            score = 0
            # 辞書とスクレイピングした単語の要素の差分をとる
            sub_counter = row['counter'] - word_counter
            # 差分がない(辞書の単語の要素 ⊃ スクレイピングした単語)かつストップワードでないか
            if sub_counter == Counter() and row['word_name'] not in stop_wordlist:
                for k, v in dict(row['counter']).items():
                    score += (v*1 if k in one_point else v*2 if k in two_points else v*3)
                score += 1
                score = score**2
                stop_count += 1
            # スコアがベストスコアを上回ったら、スコアとその単語を更新
            if score > best_score:
                best_score = score
                best_word = row['word_name']
            if stop_count > 10:
                break
        word_length -= 1
    print(best_word)
    print(best_score)
    return [best_word, best_score]

# Webページの一連の手続きを行い、打ち切るべきかどうか('No')、繰り返さなければならないか('Repeat')、正常に進んだか('Yes')判断する
def web_procedure(procedure_list : list) -> str:
    print(return_list[0])
    if return_list[1] <= 160:
        return 'No'
    print('best_word :'+str(return_list[0]))
    driver.find_element_by_xpath("//input[@id='MoveField']").send_keys(return_list[0])
    driver.save_screenshot('screen.png')
    driver.find_element_by_xpath("//input[@value='Submit']").click()
    time.sleep(0.5)
    driver.save_screenshot('screen_after_click.png')
    print(driver.find_elements_by_xpath("//p[@class='error']"))
    if driver.find_elements_by_xpath("//p[@class='error']") != []:
        return 'Repeat'
    return 'Yes'



make_dictionary()
whole_score = 0
while (whole_score < 1700):
    
    url = 'https://icanhazwordz.appspot.com/'
    driver = webdriver.PhantomJS()
    driver.get(url)
    whole_score = 0

    for var in range(0, 10):
        print(var)
        stop_wordlist = []
        data = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(data,"html.parser")
    #     print(soup)
        print(stop_wordlist)
        return_list = scrape(soup,stop_wordlist) 
        return_str = web_procedure(return_list)
        print(return_str)
        if return_str == 'Yes':
            pass
        elif return_str == 'No':
            break
        else :
            while not return_str != 'Repeat':
                print('Repeat!')
                stop_wordlist.append(return_list[0]) 
                print(stop_wordlist)
                return_list = scrape(soup,stop_wordlist) 
                return_str = web_procedure(return_list)
                print(return_str)
            if return_str == 'Yes':
                pass
            elif return_str == 'No':
                break
        whole_score += return_list[1]
    print('whole_score :'+str(whole_score))

    
driver.find_element_by_xpath("//input[@name='NickName']").send_keys('Momo')
driver.find_element_by_xpath("//input[@name='URL']").send_keys('https://github.com/momom-ito/hw1')
driver.find_element_by_xpath("//input[@name='PublicURL']").click()
driver.find_element_by_xpath("//input[@id='AgentRobot']").click()
driver.find_element_by_xpath("//input[@name='Name']").send_keys('Momo')
driver.find_element_by_xpath("//input[@name='Email']").send_keys('g1620503@is.ocha.ac.jp')
driver.save_screenshot('screen_before_send.png')
driver.find_element_by_xpath("//input[@value='Record!']").click()

