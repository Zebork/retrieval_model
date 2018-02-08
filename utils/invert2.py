# -*- coding:utf-8 -*-

"""
 ___________
< DirBuster >
 -----------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\\
                ||----w |
                ||     ||

Usage:
    invert.py <mode> [<dir>]
    invert.py -h

Options:
    -h                  show help

Example:
    invert.py 1 tencent_cache
    invert.py 2 index.pkl
    invert.py 3 tencent_cache
Command Line Example:
    inverter.search_liner('中国美国法国德国')

"""

from gevent import monkey
from gevent.lock import BoundedSemaphore
from gevent.pool import Pool
import os
from collections import defaultdict
import jieba
import Queue
import json
import time
from datetime import datetime
import threading
# from docopt import docopt
import MySQLdb
try:
    import cPickle as pickle
except ImportError:
    print 'cPinkle Error'
    import pickle
import math
from db_connecter import db_connecter
monkey.patch_all()

class tf_idf_float:
    __NUM__ = 0.0
    def __init__(self, num = 0): 
        self.__NUM__ = float(num)
    def set(self, num):
        self.__NUM__ = float(num)
    def get(self):
        return self.__NUM__
    def __str__(self):
        return str(self.__NUM__)
    def __add__(self, n):
        return self.__NUM__ + n


class Inverter:

    inverted_index = defaultdict(list)
    before_merge_queue = Queue.Queue()
    get_queue = Queue.Queue(5)
    # db_queue = Queue.Queue()
    init_stopped = False
    merge_stopped = False
    stop_tokens = set()
    NUM = 0
    FILES = []
    FILES_PATCH = []
    lock = BoundedSemaphore()
    mode = 1
    inverted_dict = dict()
    db_dumped = None

    put_num = 0
    get_num = 0


    #Mode 1: 单线程构建 Mode 2: 从文件中重构 Mode 3: 多线程构建（实际上与单线程的区别不大）

    def __init__(self, mode = 4, news_path = 'test_cache/', pkl_path='invert_index.pkl'):

        self.connecter = db_connecter()

        self.mode = mode
        if mode == 1:
            self.load_stop_tokens()
            self.init_invert(news_path)
            self.merge_invert()
            self.add_df()
            self.tf_idf_init()
        if mode == 2:
            self.load_stop_tokens()
            self.read_invert_from_file(pkl_path)
        if mode == 3:
            self.load_stop_tokens()
            # pool = Pool(2)
            threading.Thread(target=Inverter.init_invert, args=(self,news_path)).start()
            # threading.Thread(target=Inverter.merge_invert,args=(self,)).start()
            self.merge_invert()
            # pool.spawn(self.init_invert, news_path)
            # pool.spawn(self.merge_invert)
            # pool.join()
            self.add_df()
            self.tf_idf_init()
        if mode == 4:
            self.load_stop_tokens()
            self.init_invert()
            self.print_files_to_db()
            self.merge_invert_to_db()
            self.tf_idf_init_to_db()
        if mode == 5:
            pass

    def cut(self, phrase):
        return jieba.cut(phrase)

    # 获得停用词表，问题主要在如果用户查停用词怎么办
    def load_stop_tokens(self, file_path='stop_tokens2.txt'):
        ## 
        import codecs
        with codecs.open(file_path,encoding='utf-8') as f:
            tokens = f.read()
            f.close()
            tokens = tokens.rstrip('\n').split('\n')
            map(self.stop_tokens.add,tokens)
            self.stop_tokens.add(u'中国')
            self.stop_tokens.add(u'的')
            self.stop_tokens.add(u'玩')
            self.stop_tokens.add('\n')
            self.stop_tokens.add('\r')
            self.stop_tokens.add('\n\r')
            self.stop_tokens.add('....')
            self.stop_tokens.add('.....')
            self.stop_tokens.add('.......')
            self.stop_tokens.add('*')
    # 初始化队列，初始化队列的时候没有删除停用词
    def init_invert(self,file_path): #file_path是文档集的所在目录

        def init_invert_worker(self, fileID, json_content):
            # length_content = 0
            content = json.loads(json_content)
            # content_length = len(content)
            title = content['title']
            # title_length = len(title)
            text = content['content'].replace('<br>',' ')
            # content_length += len(text)
            comment_length = 0
            time_float = self.get_time(content['time'])
            # print time_float
            try:
                comments = content['comments']
                comment_length = len(comment)
            except:
                comments = []

            title_jieba = jieba.cut_for_search(title)
            text_jieba = jieba.cut_for_search(text)
            com = ''
            
            for comment in comments:
                com = com + comment['text'] + ' '
            # comment_length = len(com)
            comment_jieba = jieba.cut_for_search(com)
            cell = (fileID, title_jieba,text_jieba,comment_jieba, comment_length, time_float)

            # with self.lock:
            #     self.NUM += 1
            #     print self.NUM # 计算文档总数
            self.before_merge_queue.put(cell)
        
        files = os.listdir(file_path)
        if file_path[-1] != '/':
            file_path = file_path + '/'

        for file in files:
            if file.find('json') > 0:
                self.FILES.append(file)
        self.NUM = len(self.FILES)
        self.FILES_PATCH = [0 for i in self.FILES]
        num = 0

        # self.print_files_to_db()


        pool = Pool(50)
        for file in files:
            if file.find('json') > 0:
                # self.FILES.append(file)
                with open(file_path+file) as f:
                    json_content = f.read()
                    f.close()
                    num += 1
                    print num
                    # init_invert_worker(self, file ,json_content)
                    pool.spawn(init_invert_worker, self, file ,json_content)
        pool.join()
        # print self.FILES
        self.init_stopped = True
    # 倒排表合并
    def get_time(self, string):
        string = datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
        return time.mktime(string.timetuple())
        # print datetime.fromtimestamp(aa_float)
    def merge_invert(self):
        def count_tf(cell):
            # length = cell[4]+cell[5]+cell[6]
            count_dict = defaultdict(int) # 对TF值的计数器
            # print cell[1]
            for term in cell[1]:
                # print term
                if term in self.stop_tokens: # 删除停用词
                    # count_dict[term] += 0.1 #删除的话如果用户搜索停用词就直接没有了，不太好，暂时分配一个非常低的权重
                    continue
                else:
                    count_dict[term] += 10
            # print 
            for term in cell[2]:
                if term in self.stop_tokens: # 删除停用词
                    # count_dict[term] += 0.1
                    continue
                else:
                    count_dict[term] += 1
            for term in cell[3]:
                if term in self.stop_tokens: # 删除停用词
                    # count_dict[term] += 0.1
                    continue
                else:
                    count_dict[term] += 0.1
            for term in count_dict:
                count_dict[term] = 1 + math.log(count_dict[term])

            return count_dict

        def merge_cell(cell, index):
            count_dict = count_tf(cell)
            # print count_dict
            fileID = cell[0]
            # print fileID
            file_id_p = -1
            # for i in range(len(self.FILES)):
            #     if self.FILES[i] == fileID:
            #         file_id_p = i
            #         self.FILES_PATCH[file_id_p] = (cell[4], cell[5])
            #         break
            try:
                file_id_p = self.FILES.index(fileID)
                self.FILES_PATCH[file_id_p] = (cell[4], cell[5])
            except:
                pass
            if file_id_p == -1:
                print 'Cannot Find'

            for term in count_dict:
                # print term
                cell_str = '({},{},{});'.format(file_id_p, count_dict[term],0)
                if len(self.inverted_index[term]) == 2:
                    self.inverted_index[term][0] += 1
                    self.inverted_index[term][1] += cell_str  
                else:
                    self.inverted_index[term] = [1,'']
                    self.inverted_index[term][1] += cell_str 
            print '词项空间:' + str(len(self.inverted_index)) + '\t' + '文档数目' + str(self.NUM)
            # for key in self.inverted_index:
            #     print key
        # index = self.inverted_index


        # pool = Pool(50)
        while True:
            if not self.before_merge_queue.empty():
                cell = self.before_merge_queue.get()
                self.get_num += 1
                merge_cell(cell, self.inverted_index)
                print 'Get from queue: {}'.format(self.get_num)
                if self.get_num % 50000000 == 0: ## 删除分段功能
                    while self.get_queue.full():
                        time.sleep(5)
                    # self.write_dict_to_db()
                    self.get_queue.put(self.inverted_index)
                    self.inverted_index = defaultdict(list)
            else:
                if self.init_stopped:
                    if len(self.inverted_index) > 0:
                        while self.get_queue.full():
                            time.sleep(5)
                        self.tf_idf_init_for_simple(self.inverted_index)
                        self.get_queue.put(self.inverted_index)
                        self.write_to_file()
                        self.inverted_index = defaultdict(list)
                    break
                time.sleep(0.1)
        
        self.tf_idf_init_for_simple(self.inverted_index)
        self.print_files_to_db()
        self.merge_stopped = True
                # if self.mode == 3:
                #     time.sleep(0.2)
        # pool.join()

    def write_dict_to_db(self):
        while True:
            if self.get_queue.empty():
                if self.merge_stopped:
                    break
                time.sleep(1)
                continue
            connecter = self.connecter
            connecter.write_dict_huge_simple(self.get_queue.get())

    def print_files_to_db(self):
        if len(self.FILES) == 0:
            cache = os.listdir('news/')
            for name in cache:
                if name.find('json') > 0:
                    self.FILES.append(name)
            self.NUM = len(self.FILES)
        self.FILES_PATCH = [(1,) for x in self.FILES]
        # print self.FILES[63702]
        num = 0
        for file in self.FILES:
            with open('news/'+file) as f:
                f_c = f.read()
                f.close()
                f_j = json.loads(f_c)
                hot = 0
                try:
                    hot = len(f_j['comments'])
                except:
                    pass
                time = self.get_time(f_j['time'])
                self.FILES_PATCH[num] = (hot,time)
                print num
                num += 1
        self.connecter.print_files(self.FILES, self.FILES_PATCH)



    def merge_invert_to_db(self):
        def count_tf(cell):
            count_dict = defaultdict(int) # 对TF值的计数器
            # print cell[1]
            for term in cell[1]:
                # print term
                if term in self.stop_tokens: # 删除停用词
                    # count_dict[term] += 0.1 #删除的话如果用户搜索停用词就直接没有了，不太好，暂时分配一个非常低的权重
                    continue
                else:
                    count_dict[term] += 10
            # print 
            for term in cell[2]:
                if term in self.stop_tokens: # 删除停用词
                    # count_dict[term] += 0.1
                    continue
                else:
                    count_dict[term] += 1
            for term in cell[3]:
                if term in self.stop_tokens: # 删除停用词
                    # count_dict[term] += 0.1
                    continue
                else:
                    count_dict[term] += 0.8
            return count_dict

        def merge_cell(cell):
            count_dict = count_tf(cell)
            # print count_dict
            fileID = cell[0]
            # print fileID
            file_id_p = -1
            for i in range(len(self.FILES)):
                if self.FILES[i] == fileID:
                    file_id_p = i
                    break
            if file_id_p == -1:
                print 'Cannot Find'
            self.connecter.insert_invert_doc(count_dict,file_id_p)
                
        while True:
            if not self.before_merge_queue.empty():
                cell = self.before_merge_queue.get()
                merge_cell(cell)
            else:
                if self.init_stopped:
                    break
                else:
                    time.sleep(2)

        # pool.join()

    def tf_idf_init_to_db(self):
        if len(self.FILES) == 0: ##这里没写完！！！！
            self.files_load_from_db()
        self.connecter.tf_idf_init(self.NUM)
        
    def files_load_from_db(self):

        self.FILES, self.FILES_PATCH = self.connecter.file_reload()
        self.NUM = len(self.FILES)

    def inverted_index_dict_load(self):
        self.db_dumped = self.connecter.dump()
        for i in range(len(self.db_dumped)):
            cell = self.db_dumped[i]
            term = cell[0]
            self.inverted_dict[term] = i
        # print self.inverted_dict


    # 倒排表添加df值
    def add_df(self):
        for term in self.inverted_index:
            df = len(self.inverted_index[term][1])
            # print term + ':' + str(df)

            self.inverted_index[term][0] = df
            # print item, ' : ' , self.inverted_index[item]['doc']

    # 倒排表序列化存成文件
    def write_to_file(self,file_path = 'invert_index.pkl',index=None):
        if index == None:
            index = self.inverted_index
        with open(file_path, 'wb') as f:
            pickle.dump(index, f)
            f.close()

    # 从文件中reload倒排表
    def read_invert_from_file(self, file_path='invert_index.pkl'):
        print 'INIT INVERTED INDEX RELOAD'
        with open(file_path, 'rb') as f:
            self.inverted_index = pickle.load(f)
            f.close()
    # 倒排表添加tf-idf字段，需要在df添加后运行，否则出错
    # def tf_idf_init(self):
    #     for term in self.inverted_index:
    #         idf = math.log(float(self.NUM) / self.inverted_index[term][0])
    #         for doc in self.inverted_index[term][1]:
    #             doc[2].set(idf * doc[1])

    def tf_idf_init_for_simple(self, index):
        # if not self.get_queue.empty():
        #     index = self.get_queue.get()
            num = 0
            total = len(index)
            for term in index:
                num += 1
                print 'Termtf_idf_init {}\tin total {}.'.format(num,total)
                idf = math.log(float(self.NUM) / index[term][0])
                docs = index[term][1].split(';')
                if len(docs) > 1:
                    docs = docs[0:-1]
                doc_cache = ''
                for doc in docs:
                    doc_cell = doc.rstrip(')').lstrip('(').split(',')
                    if len(doc_cell) == 3:
                        file_id_p = doc_cell[0] #str
                        tf = float(doc_cell[1])
                        idf = math.log(float(self.NUM) / index[term][0])
                        tf_idf = str(round(idf * tf, 2))
                        doc_cache += '({},{},{});'.format(file_id_p, tf, tf_idf)
                index[term][1] = doc_cache
            # print self.inverted_index[term]['doc']

    # 基础的搜索，能得到保存完整的搜索结果，但没有合并等操作
    def search(self, search_phrase):
        # print self.inverted_index
        phrase_devided = jieba.cut_for_search(search_phrase)
        dict_cache = {}
        for term in phrase_devided:
            cache = []
            try:
                doc_chain = self.inverted_index[term][1]
                # print doc_chain
                for doc in doc_chain:
                    cache.append(doc)
                dict_cache[term] = cache
            except:
                print u'词项中不存在:' + term + u'，可能为停用词'
                continue
        return dict_cache
    def search_from_dict(self,search_phrase):
        phrase_devided = jieba.cut_for_search(search_phrase)
        dict_cache = {}
        for term in phrase_devided:
            cache = []
            try:
                index = self.inverted_dict[term]

                doc_chain = self.db_dumped[index][2]
                doc_chain_cache = doc_chain.split(';')[0:-1]
                for cell in doc_chain_cache:
                    cell = cell.lstrip('(').rstrip(')')
                    con = cell.split(',')
                    
                    doc_id_p = int(con[0])
                    df = float(con[1])
                    tf_idf = float(con[2])
                    cache.append((doc_id_p,df,tf_idf_float(tf_idf)))
            except:
                print 'search_from_dict wrong'
            dict_cache[term] = cache
        return dict_cache
    def search_from_index(self,search_phrase):
        phrase_devided = jieba.cut_for_search(search_phrase)
        dict_cache = {}
        for term in phrase_devided:
            cache = []
            try:
                # index = self.inverted_dict[term]

                doc_chain = self.inverted_index[term][2]
                doc_chain_cache = doc_chain.split(';')[0:-1]
                for cell in doc_chain_cache:
                    cell = cell.lstrip('(').rstrip(')')
                    con = cell.split(',')
                    
                    doc_id_p = int(con[0])
                    df = float(con[1])
                    tf_idf = float(con[2])
                    cache.append((doc_id_p,df,tf_idf_float(tf_idf)))
            except:
                print 'search_from_index wrong'
            dict_cache[term] = cache
        return dict_cache
    
    def search_from_db(self, search_phrase):
        phrase_devided = jieba.cut_for_search(search_phrase)
        dict_cache = {}
        # doc_chain_tuple = self.connecter.search_cache(phrase_devided)[0][0]
        # print len(doc_chain_tuple)
        num = 0
        for term in phrase_devided:
            
            # print doc_chain
            cache = []
            try:
                # index = self.inverted_dict[term]

                # doc_chain = self.db_dumped[index][2]
                doc_chain = self.connecter.search(term)
                # doc_chain = doc_chain_tuple[num]
                # print doc_chain
                doc_chain_cache = doc_chain.split(';')[0:-1]
                for cell in doc_chain_cache:
                    cell = cell.lstrip('(').rstrip(')')
                    con = cell.split(',')
                    
                    doc_id_p = int(con[0])
                    df = float(con[1])
                    tf_idf = float(con[2])
                    cache.append((doc_id_p,df,tf_idf_float(tf_idf)))
            except:
                print 'search_from_db wrong'
            print len(cache)
            dict_cache[term] = cache
            num += 1
        return dict_cache

    def search_from_db2(self, search_phrase):
        # phrase_devided = jieba.cut_for_search(search_phrase)
        if search_phrase == u' 国科大' or search_phrase == u'国科大':
            phrase_devided = jieba.cut(u'中国科学院大学')
        else:
            phrase_devided = jieba.cut(search_phrase)
        dict_cache = {}
        num = 0
        for term in phrase_devided:
            if term in self.stop_tokens:
                # print '停用词'
                continue
            cache = {}
            try:
                doc_chain = self.connecter.search(term)
                # print doc_chain
                doc_chain_cache = doc_chain.split(';')[0:-1]
                for cell in doc_chain_cache:
                    cell = cell.lstrip('(').rstrip(')')
                    con = cell.split(',')
                    doc_id_p = int(con[0])
                    df = float(con[1])
                    tf_idf = float(con[2])
                    cache[doc_id_p] = (doc_id_p,df,tf_idf_float(tf_idf))
            except:
                print 'search_from_db wrong'
            print len(cache)
            dict_cache[term] = cache
            num += 1
        return [phrase_devided, dict_cache]

    # 较强大的搜索，直接获取排序后的文档列表
    def search_liner(self, search_phrase):
        print search_phrase
        if self.mode >=4:
            dict_cache = self.search_from_db(search_phrase)
        else:
            dict_cache = self.search(search_phrase)
        doc_cache = []
        # print dict_cache
        for term in dict_cache:
            doc_chain = dict_cache[term]
            if len(doc_chain) > 700:
                print '包含停用词：{}'.format(term.encode('utf-8'))
                continue
            for doc in doc_chain:
                isset = False
                for doc_and_rank in doc_cache:
                    # print doc_and_rank
                    if doc[0] == doc_and_rank[0]:
                        # print doc, doc_and_rank
                        doc_and_rank[1] = doc[2] + doc_and_rank[1]
                        isset = True
                        break
                if isset:
                    continue
                doc_cache.append([doc[0], doc[2].get()]) # float对象，千万不能把对象本身带进去，否则搜索会改变倒排索引
                # isset = False
        # print self.NUM
        # print self.inverted_index
        print self.sort(doc_cache)
        return self.sort(doc_cache)

    def search_liner2(self, search_phrase, point='point'):
            print search_phrase

            dict_cache = self.search_from_db2(search_phrase)
            phrase_devided = dict_cache[0]
            dict_cache = dict_cache[1]
            doc_cache = {}
            # print dict_cache
            for term in dict_cache:
                doc_chain = dict_cache[term]
                if term in self.stop_tokens or len(doc_chain) > 10000:
                    print '包含停用词：{}'.format(term.encode('utf-8'))
                    continue
                for doc in doc_chain:
                    try:
                        doc_cache[doc][1] += doc_chain[doc][2]
                    except:
                        doc_cache[doc] = [doc_chain[doc][0],doc_chain[doc][2].get()]

            doc_cache = doc_cache.values()
            # print self.sort(doc_cache)
            if len(doc_cache) > 0:
                return [phrase_devided,self.sort(doc_cache, point)]
            else:
                return []

    def sort(self,cache, point='point'):
        def hot_func(self, cell):
            return self.FILES_PATCH[cell[0]][0]
        def time_func(self, cell):
            return self.FILES_PATCH[cell[0]][1]
        sorted_cache = sorted(cache, key = lambda cell: cell[1], reverse = True)
        # print self.FILES

        if point == 'hot':
            # print 1111111
            if len(sorted_cache) > 10:
                sorted_cache = sorted_cache[0:10]
            sorted_cache = sorted(cache, key = lambda cell: self.FILES_PATCH[cell[0]][0], reverse = True)
            return map(lambda x: [self.FILES[x[0]],self.FILES_PATCH[x[0]][0]], sorted_cache) 
        if point == 'time':
            if len(sorted_cache) > 10:
                sorted_cache = sorted_cache[0:10]
            sorted_cache = sorted(cache, key = lambda cell: self.FILES_PATCH[cell[0]][1], reverse = True)
            return map(lambda x: [self.FILES[x[0]],self.FILES_PATCH[x[0]][1]], sorted_cache)

        # for cell in sorted_cache:
        #     cell[0] = self.chr2int(cell[0])
        return map(lambda x: [self.FILES[x[0]],x[1]], sorted_cache) 

    def search_term(self, search_phrase):
        terms = jieba.cut(search_phrase)
        terms = [term for term in terms]
        if len(terms) > 0:
            to_find_term = terms[-1]
        connecter = self.connecter
        cache = connecter.search_term(to_find_term)
        terms_before = terms[0:-1]
        terms_before = ''.join(terms_before)
        ret_cache = []
        for cell in cache:
            if cell[0] == to_find_term:
                continue
            dic = {'name':terms_before + cell[0]}
            ret_cache.append(dic)
        return ret_cache

    def get_hot_list(self, order):
        hot_list = self.connecter.get_hot_list(order)
        return hot_list


        # return sorted_cache
## 重新建立
# my_inverter = inverter()
# my_inverter.load_stop_tokens()
# my_inverter.init_invert('tencent_cache')
# my_inverter.merge_invert()
# my_inverter.add_df()
# my_inverter.tf_idf_init()
# my_inverter.write_to_file()

## 从文件中读取倒排索引
if __name__ == "__main__":
    inverter = Inverter(mode=5)
    inverter.load_stop_tokens()
    # inverter.print_files_to_db()
    # inverter.files_load_from_db()
    # print inverter.get_hot_list()
    # inverter.print_files_to_db()
    # threading.Thread(target=Inverter.init_invert, args=(inverter,'news_cache_new/')).start()
    # threading.Thread(target=Inverter.merge_invert,args=(inverter,)).start()
    # # inverter.tf_idf_init_for_simple()
    # inverter.write_dict_to_db()
    # print 'OK'
    # inverter.print_files_to_db()
    # inverter.merge_invert_to_db()
    # inverter.files_load_from_db()
    # # inverter.tf_idf_init_to_db()
    # # inverter.inverted_index_dict_load()
    # # inverter.search_liner('奥迪')
    # time.sleep(5)
    # inverter.search_term(u'奥迪')
    # inverter.search_liner('tel')
#     arguments = docopt(__doc__, version="1.0")
#     mode = int(arguments["<mode>"])
#     dir_file = arguments["<dir>"]
#     if mode in [1,2,3]:
#         print """Loading... 
# This may take a lot of time.
# Have a cup of coffee.
# Good Luck!
# """
#         if mode ==1 or mode ==3:
#             if dir_file == None:
#                 dir_file = inverter = Inverter(mode=mode)
#             else:
#                 inverter = Inverter(mode=mode,news_path=dir_file)
#         if mode == 2:
#             if dir_file == None:
#                 dir_file = 'invert_index.pkl'
#             inverter = Inverter(mode=mode,pkl_path=dir_file)
#         inverter.search_liner('中国')
#         print """Usage:
#             inverter.search_liner('中国美国法国德国')"""
#         import code
#         code.interact(local=locals())

