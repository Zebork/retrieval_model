# -*- coding:utf-8 -*-
import os
import spiders.toutiao as toutiao
import spiders.tencent as tencent
from utils.db_connecter import db_connecter
from utils.invert2 import Inverter
from datetime import date, timedelta, datetime
import time
import threading
from gevent import monkey
from gevent.lock import BoundedSemaphore
from gevent.pool import Pool
import json
import random
from jieba import analyse
import jieba
from utils.csvm import comments_classify as comments_classify
inverter = Inverter(mode=5) 

monkey.patch_all()

def toutiao_spider(mode=None):
    if mode == None:
        mode = 1
    if mode == 1:
        toutiao.autorun()
    if mode == 2:
        toutiao.depart()
    if mode == 3:
        toutiao.patch()

def tencent_spider(mode=None):
    if mode == None:
        mode = 1
    if mode == 1:
        tencent.autorun()
    if mode == 2:
        tencent.depart()
    if mode == 3:
        tencent.patch()

def merge_news():
    to_carry_dir = u'news_cache/'
    to_carry_list = os.listdir(to_carry_dir)
    to_carry_list = set(to_carry_list)
    aim_dir = u'news/'
    aim_list = os.listdir(aim_dir)
    aim_list = set(aim_list)
    to_carry_list = to_carry_list - aim_list
    for file in to_carry_list:
        if file.find('json') > 0:
            with open(to_carry_dir + file) as f:
                file_content = f.read()
                f.close()
                with open(aim_dir + file, 'w') as f2:
                    print file
                    f2.write(file_content)
                    f2.close()
def files_redo():
    inverter.load_stop_tokens()
    inverter.print_files_to_db()

def invert_redo():
    inverter.load_stop_tokens()
    threading.Thread(target=Inverter.init_invert, args=(inverter,'news/')).start()
    threading.Thread(target=Inverter.merge_invert,args=(inverter,)).start()
    inverter.write_dict_to_db()

def invert_load():
    inverter.load_stop_tokens()
    inverter.files_load_from_db()
    inverter.search_liner2('奥巴马')
def check_not_null():
    connecter = db_connecter()
    return connecter.check_not_null()
def delete_inverted():
    return connecter.delete_inverted()

def get_term(search_phrase):
    invert_load()
    return inverter.search_term(search_phrase)

def get_detail(query, target):
    if type(target) == type(u'a'):
        target = target.decode('utf-8')
    print type(target)
    ret = {}
    with open('news/{}'.format(target)) as f:
        file_content = f.read()
        # print file_content
        f.close()
        file_content = json.loads(file_content)
        # print file_content
        title = file_content['title']
        # print title
        content = file_content['content']
        for term in inverter.cut(query):
            if term in inverter.stop_tokens:
                continue
            content = content.replace(term, '<em>'+term+'</em>')
        ret['title'] = title
        ret['content'] = content.lstrip('[').lstrip('\n').lstrip(']')
        try:
            comments = file_content['comments']
            ret['comments'] = comments
        except:
            pass
        return json.dumps(ret)

def get_hot_list(order):

    hot_list = inverter.get_hot_list(order)
    cache = []
    for cell in hot_list:

        with open('news/'+cell[0]) as f:
            a = f.read() 
            a = json.loads(a)
            f.close()
            
            b = {}
            # print time.clock()
            b['url'] = a['url']
            # print time.clock()
            b['title'] = a['title']
            b['local_url'] = "./news?name="+cell[0].encode('base64')
            b['time'] = datetime.fromtimestamp(cell[2]).strftime('%Y-%m-%d %H:%M:%S')
            b['remarks'] = cell[1]
            
            cache.append(b)
    return cache

def sim_recomm(json_content, name=None):
    def check(string, cache):
        for cell in cache:
            print type(cell[0])
            if string == cell[0]:

                return True
        return False
    # content = json.loads(json_content)
    content = json_content
    title = content['title'] 
    text = content['content'].replace('<br>',' ')

    try:
        comments = content['comments']
    except:
        comments = []

    tags = jieba.analyse.extract_tags(text, topK=5)

    sim_news = []
    res = inverter.search_liner2(title)
    # print "res[1][0] {}".format(res[1][0])
    if len(res[1]) <= 1 :
        if len(res[1]) == 1 :
            return res[1][0]
        else:
            return False
    x = 0
    while x < 2 :
        index = [random.randint(0,4) for _ in range(3)]
        comp_text = tags[index[0]]+','+tags[index[1]]+','+tags[index[2]]
        res = inverter.search_liner2(comp_text)
        if x ==0:
            if res[1][0][0] == name:
                sim_news.append( res[1][1] )
                sim_news.append( res[1][2] )
            elif res[1][0][1] == name:
                sim_news.append( res[1][0] )
                sim_news.append( res[1][2] )
            else:
                sim_news.append( res[1][0] )
                sim_news.append( res[1][1] )
        else:
            num = 0
            for it in res[1]:
                if it[0] == name or check(it[0],sim_news):
                    continue
                else:
                    sim_news.append(it)
                    num += 1
                if num == 2:
                    break
        x = x + 1
    return sim_news

def spa(data):
    return comments_classify(data)

def main():
    files_redo()

if __name__ == "__main__":
    main()
# print date.today()#(today - timedelta(x)).strftime('%Y-%m-%d') 

