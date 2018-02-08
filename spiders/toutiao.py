#-*- coding:utf-8 -*-

import requests
import yaml
import json
import threading
import time
import Queue
import logging
from lxml import etree
from gevent import monkey
from gevent.lock import BoundedSemaphore
from gevent.pool import Pool
import os
import random
from datetime import date, timedelta

monkey.patch_all()

logging.basicConfig(level=logging.INFO)


# class toutiao:

# 今日头条的频道
category = [
'articles_news_entertainment','articles_news_tech','articles_digital',
'articels_news_sports','articles_news_finance','articles_news_military',
'articles_news_culture','articles_science_all', 'articles_news_car',
'articles_news_world', 'articles_news_travel', 'articles_news_game',
'articles_news_fashion', 'articles_news_history','articles_news_discovery',
'articles_news_regimen','articles_news_food','articles_news_society'
]



before_queue = Queue.Queue() # 并非需要IO的队列
to_do_queue = Queue.Queue() # 准备进行解析的新闻页面入队
to_save_queue = Queue.Queue()


global_news_id = 1 # 文档ID 文档ID加锁 防止竞争
parse_stopped = False
stopped = False
save_lock = BoundedSemaphore()
toutiao = 'https://www.toutiao.com' # base url

# direct = None
# proxy1 = {'http':'http://10.211.55.3:1080',}
# proxy_choice = [direct,proxy1,proxy1,proxy1,proxy1,proxy1,proxy1]


def my_requests(url = None, headers=None):
    times = 0
    while True:
        try:
            r = requests.get(url, headers = headers,timeout=7)
            # print r.text
            if r.status_code == 500:
                print '500'
                continue
            else:
                return r

        except:
            times += 1
            if times > 6:
                logging.info('Connect Error')
                return False
            time.sleep(2)
            continue
def get_content(url):

    def get_comment(group_id, item_id):
        comment_url = 'https://www.toutiao.com/api/comment/list/?group_id={}&item_id={}&offset=0&count=100'.format(group_id,item_id)
        headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
        comment_content = my_requests(comment_url,headers=headers).content
        try:
            json_comment = json.loads(comment_content)
            if json_comment["data"]["total"] == 0:
                return None
            else:
                return json_comment
        except:
            return None
    base_url = url
    logging.info('get_connect...{}'.format(base_url))
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
    test = my_requests(base_url,headers=headers)
    if test == False:
        return
    if test.status_code == 301:
        return

    test_html = test.content
    start = test_html.find('BASE_DATA')
    end = test_html[start:].find('</script>') + start
    json_content = test_html[start+12:end].rstrip(';')
    # print json_content
    while json_content.find('.replace') > 0:
        error_code_start = json_content.find('.replace')
        error_code_end = json_content[error_code_start:].find('),') + error_code_start
        json_content = json_content[0:error_code_start] + json_content[error_code_end+1:]
    new_comments = []
    try:
        json_obj= yaml.load(json_content)
    except:
        return None
    try:
        group_id = json_obj['articleInfo']['groupId']
        item_id = json_obj['articleInfo']['itemId']
        json_comment = get_comment(group_id,item_id)
        if json_comment != None:
            # new_comments = []
            json_comment = json_comment["data"]["comments"]
            for cell in json_comment:
                new_cell = {"text": cell["text"]}
                create_time = {"create_time": cell["create_time"]}
                new_cell.update(create_time)
                user_id = cell["user"]["user_id"]
                user_name = cell["user"]["name"]
                new_cell.update({"user_id":user_id})
                new_cell.update({"user_name":user_name})
                new_comments.append(new_cell)
            json_comment = new_comments

    except:
        json_comment= None

    if json_comment == None:
        comment_cell = None
    else:
        comment_cell = {"comments": json_comment}

    try:
        site = json_obj['headerInfo']['chineseTag']
        init_cell = {"url": base_url}
        init_cell.update({"source":u'今日头条'})
        init_cell.update({"source_tab":'toutiao'})
        init_cell.update({"site":site})
        news_title = {"title":json_obj["articleInfo"]["title"]}
        news_content = json_obj["articleInfo"]["content"]
        news_time = json_obj["articleInfo"]["subInfo"]["time"]
        news_time = {"time": news_time}
        news_content = news_content.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace('&#39;',"'").replace('&quot','"').replace('&#x3D;";','=').replace('";','')
        if len(news_content) < 2:
            print 'wrong'
            return
        news_content = {"content":news_content}
        init_cell.update(news_title)
        init_cell.update(news_content)
        init_cell.update(news_time)
        if comment_cell != None:
            init_cell.update(comment_cell)

        my_news_id = base_url.lstrip(toutiao).rstrip('/')
        security_num = my_news_id.find('/')
        if security_num >= 0:
            my_news_id = my_news_id[0:security_num] + '_' + my_news_id[security_num+1:]
        filename = 'news/' + str(my_news_id) + '.json'
        file_content = json.dumps(init_cell)

        cell = (filename,file_content)
        # print '\n\nput\n\n'
        to_save_queue.put(cell)
    except:
        print 'except'
        return

def get_page(ca_num=0,max_page=2):
    base_page = 'https://toutiao.com/' + category[ca_num]

    for i in range(max_page):
        page_url = base_page + '/p' + str(i+1)
        # yield parse_page(page_url)
        before_queue.put(page_url)

def parse_page(page_url= None):
    # print 'start parse'
    logging.info('parse_page:' + page_url)
    times = 0
    while True:
        try:
            headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
            page_content = my_requests(page_url,headers=headers).content
            break
        except:
            return None
    page_etree = etree.HTML(page_content)
    if page_etree.xpath('//title/text()')[0].find('404') >= 0:
        return None
    # print page_url
    queue_put_thread(page_etree.xpath("//div[@class='info']//a/@href"))

def queue_put_worker():
    logging.info('putting worker started')
    pool = Pool(20)
    # max_page = 20
    while not before_queue.empty():
        cache = pool.spawn(parse_page, before_queue.get())
    pool.join()
    global parse_stopped
    parse_stopped = True

def queue_put_thread(cache):
    def add_base(url):
        url = toutiao + url
        return url
    # print cache
    if cache != None:
        cache = map(add_base, cache)
        map(to_do_queue.put, cache)


def queue_get_worker():
    pool = Pool(100)
    # pool.spawn(save_thread)
    while (not parse_stopped) or (not to_do_queue.empty()):
        if to_do_queue.empty():
            time.sleep(5)
            continue
        page_url = to_do_queue.get()
        pool.spawn(get_content, page_url)
    pool.join()
    global stopped
    stopped = True

def save_thread():
    while True:
        if not to_save_queue.empty():
            cell = to_save_queue.get()
            # print cell[0]
            with save_lock:
                with open(cell[0],'w') as f:
                    f.write(cell[1])
                    f.close()
        else:
            if stopped:
                break
            time.sleep(3)
def save_worker():
    pool = Pool(1)
    global stopped
    while not stopped:
        pool.spawn(save_thread)
    pool.join()

def before_queue_init():
    max_page = 30
    for ca_num in range(len(category)):
        get_page(ca_num, max_page)

def to_do_list_reload(file = None):
    if file == None:
        file = 'to_do_list_20171222_23-15.txt'
    with open(file) as f:
        urls = f.read()
        f.close()
        cache = urls.split('\n')
        cache = cache[0:-1]
        cache = set(cache)
        map(to_do_queue.put, cache)
        with open('to_do_list_cache.txt','w') as f2:
            for s in cache:
                f2.write(s + '\n')
            f2.close()

def to_do_list_save_worker(file = None):
    if file == None:
        file = 'to_do_list_20171215_21-02.txt'
    with open(file,'w') as f:
        while not parse_stopped:
            if not to_do_queue.empty():
                url = None
                url = to_do_queue.get()
                if url != None:
                    f.write(url+ '\n')
            else:
                time.sleep(5)
        f.close()

def autorun():
    before_queue_init()
    threading.Thread(target=queue_put_worker).start()
    time.sleep(4)
    threading.Thread(target=queue_get_worker).start()
    time.sleep(4)
    threading.Thread(target=save_thread).start()

def depart():
    today = date.today()
    to_do_list_name = 'toutiao_'+today.strftime('%Y-%m-%d') + '.txt'
    before_queue_init()
    threading.Thread(target=queue_put_worker).start()
    time.sleep(2)
    to_do_list_save_worker(to_do_list_name)

def patch():
    today = date.today()
    to_do_list_name = 'toutiao_'+today.strftime('%Y-%m-%d') + '.txt'
    to_do_list_reload(to_do_list_name)
    global parse_stopped
    parse_stopped = True
    threading.Thread(target=queue_get_worker).start()
    threading.Thread(target=save_thread).start()
def main():
    autorun()


if __name__ == "__main__":
    main()



# print json.dumps(news_url)



