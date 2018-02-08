# -*- coding:utf-8 -*-

from controller import inverter
import controller
import web
import json
import jieba
import time
# import re

sock_urls = (
    '/search', 'search',
    '/terms','terms',
    '/details','details',
    '/hots','hots',
    '/news','news',
)

class search:
    def GET(self):

        def get_phrases(phrase):
            phrases = inverter.search_term(phrase)
            return json.dumps(phrases)

        user_data = web.input()
        print user_data
        try:
            phrase = user_data.phrase
            return get_phrases(phrase)
        except:
            pass
        point =  user_data.point
        # print 'hahahah'+point 
        values = inverter.search_liner2(user_data.q, point=point)

        try:
            if len(values[1]) == 0:
                return '[]'
        except:
            return '[]'
        try:
            page = user_data.page
            try:
                page = int(page)
            except:
                return None
            return self.opener(values,user_data.q,page)
        except:
            return self.opener(values,user_data.q)
    def opener(self, values, data, page=1):
        print type(data)
        data_cache = jieba.cut(data)
        data = []
        for term in data_cache:
            data.append(term)
        phrase_devided = values[0]
        values = values[1]
        start = (page-1) * 10
        end = start + 10
        cat_range = range(start, end)
        value_length = len(values)
        # print start
        cache = []
        if value_length <= start:
            return '[]'
        for i in cat_range:
            if i >= value_length:
                break
            cell_dict = {}
            with open('news/{}'.format(values[i][0])) as f:
                file_json = json.load(f)
                f.close()
                cell_dict['url'] = file_json['url']
                title = file_json['title']
                cell_dict['title'] = file_json['title']
                content = file_json['content'].replace('<br>',' ').replace('[ ]','') 
                # print type(content)
                for term in data:
                    if term in controller.inverter.stop_tokens:
                        continue
                    red_term = u'<em>{}</em>'.format(term)
                    content = content.replace(term, red_term)
                # print content
                if len(content) > 120:
                    s = content.find('<em>')
                    if s-30 > 0:
                        content = content[s-30:s+190]
                    else:
                        content = content[s:120]
                cell_dict['content'] = content.rstrip('m').rstrip('e').rstrip('<') + ' ...'
                cell_dict['name'] = values[i][0].encode('base64')
                cell_dict['local_url'] = "./news?name=" + values[i][0].encode('base64')
            cache.append(cell_dict)
        if len(cache) == 0:
            return '[]'
        return json.dumps(cache)

class terms:
    def GET(self):
        user_data = web.input()
        return "Hello, world2!"      

class details:
    def GET(self):
        user_data = web.input()
        try:
            file_content = '[]'
            file_name = user_data.req
            query = user_data.q
            if file_name != None:
                if len(file_name) > 0:
                    file_content = controller.get_detail(query,file_name.decode('base64'))
            return file_content
        except:
            return '[]'
class hots:
    def GET(self):
        user_data = web.input()
        try:
            order = user_data.order
            if order == "comments":
                print order
                order = 1
            elif order == "time":
                order = 2
            # print time.clock()
            cache = controller.get_hot_list(order)
            # print time.clock()
            cache =json.dumps(cache)
            
            return cache
        except:
            print "hots order wrong"
class news:
    def GET(self):
        user_data = web.input()
        try:
            file_name = user_data.name
            file_name = file_name.decode('base64')
            with open('news/'+file_name) as f:
                a = f.read()
                f.close()
                json_a = json.loads(a)
                try:
                    comments = json_a["comments"]
                    if len(comments) > 10:
                        comments = comments[0:10]
                    b = map(lambda x: x["text"], comments)
                    sp = controller.spa(map(lambda x: x.encode('gb2312'), b))
                    num = 0
                    for comment in comments:
                        if sp[num] == 1:
                            comment['goodbad'] = 'Good'
                        else:
                            comment['goodbad'] = 'Bad'
                        num += 1
                    json_a["comments"] = comments
                except:
                    print 'Wrong1---1--121-201-021'
                    pass
                to_do_list = controller.sim_recomm(json_a, name=file_name)
                cache = []
                for cell in to_do_list:
                    dic = {}
                    with open('news/'+cell[0]) as f2:
                        it = json.load(f2)
                        f2.close()
                        dic['url'] = it['url']
                        dic['local_url'] = './news?name='+cell[0].encode('base64')
                        dic['title'] = it['title']
                        cache.append(dic)
                json_a['related'] = cache
                # print json_a
                dum = json.dumps(json_a)
                # print dum
                return dum
        except Exception as inst:
            print inst.args
            return '[]'

def init():
    controller.invert_load()

def start():
    app = web.application(sock_urls, globals())
    app.run()

if __name__ == "__main__":
    init()
    start()
