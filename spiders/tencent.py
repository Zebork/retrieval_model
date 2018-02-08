# -*- coding:utf-8 -*-
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
from datetime import date, timedelta
import random
import re
pattern = re.compile(r'<p>(.*?)</p>')
monkey.patch_all()
logging.basicConfig(level=logging.INFO)
to_do_queue = Queue.Queue()
to_save_queue = Queue.Queue()
to_do_list_stopped = False
get_stopped = False
sites = ['news', 'ent', 'finance','tech', 'games', 'auto']
sites += ['sports','edu','house']
proxy1 = {'http':'http://10.211.55.3:1080'}

direct = None
proxy1 = None
proxy_choice = [direct,proxy1,proxy1,proxy1,proxy1,proxy1,proxy1]

headers = {
# 'Accept-Language:':'zh-CN,zh;q=0.9,en;q=0.8,es-419;q=0.7,es;q=0.6',
'Cookie':'pgv_pvi=4346527744; RK=lBVeEw7bcK; tvfe_boss_uuid=30980d28bc3fcc55; pac_uid=1_276359212; 3g_guest_id=-8813509748168024064; ts_uid=4020831670; g_ut=2; pgv_pvid=5286402175; o_cookie=276359212; ptcz=55c46ae06e6cec2f58c85ccda63ce46834799bb37cd3bf83a9a85ec69a9023c3; pt2gguin=o0276359212; ts_refer=ent.qq.com/a/20171220/016056.htm; ptui_loginuin=xflyray@163.com; ptag=|/; pgv_info=ssid=s7707204799; ts_last=news.qq.com/; pt_local_token=123456789; ad_play_index=27',
'Host':'roll.news.qq.com',
'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
'Cache-Control':'no-cache',
'Referer':'http://news.qq.com/articleList/rolls/'
}
done = []
# headers = {'Referer':'http://news.qq.com/articleList/rolls/'}

# sites = ['edu', 'house','sports']
# base_url = 'http://roll.news.qq.com/interface/cpcroll.php?callback=rollback&site=news&mode=1&cata=&date=2017-12-06&page=2&_=1513351080701'

def reload_done(file_dir):
    global done
    done = os.listdir(file_dir)
    done = done + os.listdir('')
    # done = done + os.listdir('')
    done_set = set(done)
    return done_set
def my_sleep(sec = None):
    if sec == None:
        sec = 0.5
    time.sleep(sec)

def get_date():
    one_year = 20
    cache = []
    today = date.today()
    cache = [(today - timedelta(x)).strftime('%Y-%m-%d') for x in range(one_year)]
    return cache

def my_requests(url = None, headers=None):
    times = 0
    while True:
        try:
            r = requests.get(url, headers = headers,allow_redirects=False,timeout=10, proxies=random.choice(proxy_choice))
            if r.status_code == 500:
                times += 1
                continue
            if len(r.text) > 2:
                return r
            else:
                logging.info('Connect Error Retrying')
                time += 1
                # my_sleep()
                continue

        except:
            times += 1
            if times > 3:
                logging.info('Connect Error')
                return False
            my_sleep()
            continue

def my_json_loads(content):
    content = content.rstrip('\n').rstrip(')').lstrip('rollback(')
    while True:
        try:
            json_content = json.loads(content)
            break
        except ValueError, args:
            a = args.message

            # print a
            start = args.message.find('char')
            if start > 0:
                a = a[start+5:].rstrip(')')
                content = content[0:int(a)]+ content[int(a)+1:]
                continue
            else:
                return False
        except:
            return False
    return json_content


def to_do_queue_init():
    def parse_before(url, content):
        json_content = my_json_loads(content)
        if json_content == False:
            return False
        try:
            count = json_content['data']['count']
            return count
        except:
            return False
    def parse_list(base_url, content, site, day, count):

        cache = []
        for i in range(1, count+1):
            if i == 1:
                json_content = my_json_loads(content)
                if json_content == False: #第一次判断count时候已经拿到了第一页的数据
                    return
            else:
                url = base_url.format(site,day,i)

                logging.info('Connecting' + url)
                global headers
                r = my_requests(url,headers=headers)
                my_sleep()
                if r == False:
                    print url ,' list wrong'
                    continue
                content = r.text
                if len(content) <= 1:
                    logging.info('content is too small')
                    continue
                json_content = my_json_loads(content)
                if json_content == False:
                    print content
                    print 'json_content wrong when parse_list'
                    continue
                # print content
            pigs = json_content['data']['article_info']
            for pig in pigs:
                news_url = pig['url']
                news_title = pig['title']
                news_time = pig['time']
                dic = {'url':news_url, 'title':news_title, 'time':news_time}
                cache.append(dic)
        map(to_do_queue.put, cache)

    def to_do_queue_init_worker(day,site=None):
        # headers = {'Referer':'http://news.qq.com/articleList/rolls/'}
        global headers
        # base_url = 'http://roll.news.qq.com/interface/cpcroll.php?site={}&date={}&page={}'
        base_url = 'http://roll.news.qq.com/interface/cpcroll.php?callback=rollback&site={}&mode=1&cata=&date={}&page={}&_=1513418455308'
        if site == None:
            site = 'news'
        url = base_url.format(site,day,1)
        # print url
    # from datetime import date, timedelta
        logging.info('Connecting' + url)
        this_headers = headers
        r = my_requests(url, headers = this_headers)
        if r == False:
            print url ,' ++++ wrong'
            return
        content = r.text
        # print content
        my_sleep()
        count = parse_before(url, content)
        if count == False:
            return
        parse_list(base_url,content,site,day, count)

    days = get_date()
    pool = Pool(20)
    for site in sites:
        for day in days: 
            pool.spawn(to_do_queue_init_worker,day,site)
            # my_sleep(4)
    pool.join()
    global to_do_list_stopped
    to_do_list_stopped = True

def to_do_queue_save_thread(file=None):
    if file == None:
        file = 'tencent_20171216_18_31_sports_edu_house.txt'
    with open(file,'w') as f:
        while True:
            if not to_do_queue.empty():
                f.write(json.dumps(to_do_queue.get()) + '\n')
            else:
                if to_do_list_stopped:
                    break
                my_sleep()
        f.close()

def get_content():

    def get_pic_content(url):
        base_url = url.rstrip('html').rstrip('htm') + 'hdBigPic.js'
        logging.info('Try pic -- {}'.format(base_url))
        # print base_url
        r = my_requests(base_url, headers = None)
        if r == False:
            return []
        r_text = r.text
        content = pattern.findall(r_text)
        # print content
        return content

    def get_comment(url, page_id):

        def get_comment_num(url, page_id):
            this_headers = headers
            this_headers['Referer'] = url
            this_headers['Host'] = 'coral.qq.com'
            # print page_id

            base_url = 'https://coral.qq.com/article/{}/commentnum?callback=_cbSum&source=1&t=0.2768719206563681&callback=comment&_=1513426450180'.format(page_id)
            num_dumped = my_requests(base_url,headers=this_headers)
            # print num_dumped
            if num_dumped == False:
                return False
            com = num_dumped.text
            # print com
            com = com.rstrip(')').lstrip('comment(')
            content_num_pig = my_json_loads(com)
            if content_num_pig == False:
                return False
            if content_num_pig['errCode'] == 0:
                content_num = content_num_pig['data']['commentnum']
            else:
                return False
            return content_num # 注意这个返回的是str类型，但是拼接，没有必要转了



        comment_num = get_comment_num(url, page_id)
        print comment_num
        # print comment_num
        if comment_num == False or comment_num == "0":
            return False
        this_headers = headers
        this_headers['Referer'] = 'http://page.coral.qq.com/coralpage/comment/news.html'
        this_headers['Host'] = 'coral.qq.com'

        base_url = b ='http://coral.qq.com/article/{}/\
comment/\
v2?callback=jQuery112407956042145886819_1513427959559\
&orinum=10&oriorder=o\
&pageflag=1&cursor=\
{}&scorecursor=0\
&orirepnum=2&reporder=o&reppageflag=1&source=1&_=1513352189330'

        start_url = base_url.format(page_id, 0)
        cache = []
        while True:
            logging.info(start_url)
            r = my_requests(start_url, headers=this_headers)
            max_num = 0
            if r != False:
                max_num += 1
                json_dumped = r.text
                # print json_dumped
                json_dumped = json_dumped.rstrip('\n').rstrip(')').lstrip('\n').lstrip('jQuery112407956042145886819_1513427959559(')
                json_comments = my_json_loads(json_dumped)
                if json_comments and json_comments['errCode'] == 0:
                    if json_comments['data']['oritotal'] == 0:
                        return cache
                    hasnext = json_comments['data']['hasnext']
                    coms = json_comments['data']['oriCommList']
                    for com in coms:
                        create_time = com['time']
                        user_id = com['userid']
                        com_content = com['content']
                        com_cell = {'text': com_content,'create_time':int(create_time),'user_id':user_id}
                        cache.append(com_cell)
                    if not hasnext or max_num > 100:
                        break
                    last = json_comments['data']['last'] # 不用再判断last了，hasnext够用
                    # if last == False
                    start_url = base_url.format(page_id,last)
        if len(cache) > 0:
            return cache
        else:
            return None


    json_dumped = to_do_queue.get()
    # print json_dumped
    content_pig = my_json_loads(json_dumped)
    # print content_pig
    if content_pig == False:
        return None
    url = content_pig['url']
    filename = url.lstrip('https://')
    # print filename
    filename = filename[filename.find('/')+1:]
    filename = filename.replace('/','_').rstrip('.html').rstrip('.htm')
    filename = filename + '.json'
    if filename in done:
        return
    if url.find('http://') >= 0:
        url = url.lstrip('http://')
        url = 'https://' + url
    this_headers = {'Cookie':headers['Cookie']}
    logging.info('get_content' + url)
    r = my_requests(url, headers = this_headers)
    if r == False:
        return None
    content = r.text
    content_tree = etree.HTML(content)
    contents = content_tree.xpath("//div[@id='Cnt-Main-Article-QQ']/p/text()")
    if len(contents) == 0:
        contents = content_tree.xpath("//div[@class='content-article']/p/text()")
        if len(contents)==0:

            contents = get_pic_content(url)
            if len(contents) == 0:
                logging.info('Get_content Error ---- ' + url)
                return
    page_content = '<br>'.join(contents)
    content_dict = {'content':page_content}
    p = content
    index = p.find('cmt_id = ')
    page_id = None
    if index > 0:
        p = p[index:]
        end = p.find(';')
        page_id = p[9:end]
    else:
        p = content
        index = p.find('comment_id')
        if index > 0:
            p = p[index+13:]
            end =p.find('"')
            p = p[:end]
            page_id = p
        else:
            index = p.find('aid:')
            if index > 0:
                p = p[index+6:]
                end = p.find('"')
                p = p[:end]
                page_id = p
                
    comments = None
    comments_dict = None
    if page_id != None:
        comments = get_comment(url, page_id)
    # print comments
        comments_dict = {'comments':comments}

    content_pig.update(content_dict)
    # content_pig.update(channel_dict)
    if not (comments == None or comments == False):
        content_pig.update(comments_dict)
    cell = (filename,json.dumps(content_pig))
    to_save_queue.put(cell)

def get_thread():
    pool = Pool(400)
    while True:
        if to_do_queue.empty():
            break
        # my_sleep()
        pool.spawn(get_content)
    pool.join()
    global get_stopped
    get_stopped = True
def to_do_queue_reload(file_path):
    with open(file_path) as f:
        content = f.read()
        f.close()
        content = content.split('\n')[0:-1]
        # content = set(content
        map(to_do_queue.put, content)

def save_thread():
    while True:
        if to_save_queue.empty():
            if get_stopped:
                break
            time.sleep(5)
        cell = to_save_queue.get()
        with open('news/' + cell[0], 'w') as f:
            f.write(cell[1])
            f.close()
def autorun():
    threading.Thread(target=to_do_queue_init).start()
    time.sleep(3)
    threading.Thread(target=get_thread).start()
    time.sleep(3)
    threading.Thread(target=save_thread).start()

def depart():
    today = date.today()
    to_do_list_name = 'tencent_'+today.strftime('%Y-%m-%d') + '.txt'
    threading.Thread(target=to_do_queue_init).start()
    time.sleep(4)
    threading.Thread(target=to_do_queue_save_thread, args=(to_do_list_name,)).start()
def patch():
    today = date.today()
    to_do_list_name = 'tencent_'+today.strftime('%Y-%m-%d') + '.txt'
    # reload_done('news_cache')
    to_do_queue_reload(to_do_list_name)
    threading.Thread(target=get_thread).start()
    time.sleep(4)
    save_thread()


def main():
    # threading.Thread(target=to_do_queue_init).start()
    # time.sleep(3)
    # threading.Thread(target=to_do_queue_save_thread).start()
    # to_do_queue.put('{"url": "https://news.qq.com/a/20171216/013457.htm", "time": "2017-12-16 07:26:03", "title": "\u7f8e\u672f\u8003\u8bd5\u4f5c\u5f0a\u9690\u5f62\u8d34\u7f51\u7edc\u6708\u9500\u5343\u7b14\uff1a\u4e00\u5bf8\u5927\u5c0f"}')
    # get_content()
    reload_done('news_cache1/')
    to_do_queue_reload('tencent_20171216_16_47.txt')
    threading.Thread(target=get_thread).start()
    my_sleep()
    # threading.Thread(target=save_thread).start()
    save_thread()

if __name__ == "__main__":
    main()
