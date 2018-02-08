# -*- coding: utf-8 -*- 
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
# from os.path import abspath, join, dirname
# import sys
# sys.path.insert(0, join(abspath(dirname(__file__)), '../'))
# import controller
import requests
import json
from datetime import datetime
def hello(request):
    # return HttpResponse("Hello world ! ")
    query = request.GET.get('q')
    # page = request.GET.get('page')
    context = {}
    context['hello'] = 'Hello World!'
    context['cell_list'] = []
    cell_list = context['cell_list']
    cell_list.append({'title':'你好','url':'https://www.example.com'})
    content = u'<em>你好</em> 《<em>JJ</em>》 J2，<wbr>無線電視的一條標清數碼廣播頻道。 游戏. JJOnline。 器官. 男性生殖器官. 物理概念. <em>j-j</em>耦合&nbsp;...'
    cell_list[0]['content'] = content
    return render(request, 's.html', context)

def search(request):
    news = request.GET.get('news')
    if news == u'查看热搜':
        return HttpResponseRedirect('/hots?order=time')
    phrase = request.GET.get('phrase')
    if phrase != None:
        phrases = requests.get('http://127.0.0.1:50000/search?phrase={}'.format(phrase.encode('utf-8')))
        return HttpResponse(phrases.text)


    query = request.GET.get('q')
    page = request.GET.get('page')
    context = {}
    context['query'] = query
    if page == None or page == '':
        page = '1'
    context['page'] = page
    point = int(page) % 10
    if point == 0:
        point += 9
    else:
        point -= 1
    sort = request.GET.get('point')  
    if int(page) % 10 == 0:
        start = int(page) - 9
    else:
        start = int(page) / 10 * 10 + 1
    context['start'] = str(start)
    params = {}
    if not (query == None or query == ''):
        params['q'] = query
    if not (page == None or page == ''):
        params['page'] = page
    if not (sort == None or sort == ''):
        context['sort'] = sort
        params['point'] = sort
    else:
        context['sort'] = 'relative'
        params['point'] = 'relative'
    if context['sort'] == 'relative':
        context['check1'] = 'checked'
    elif context['sort'] == 'hot':
        context['check2'] = 'checked'
    elif context['sort'] == 'time':
        context['check3'] = 'checked'
    else:
        context['check1'] = 'checked'


    json_dumped = requests.get('http://127.0.0.1:50000/search',params=params).text
    term_params = {'phrase':query}
    terms = requests.get('http://127.0.0.1:50000/search',params=term_params).text

    print json_dumped
    # if len(json_dumped) == 0
    values = json.loads(json_dumped)
    terms = json.loads(terms)
    if len(terms) > 1:
        context['term1'] = terms[0]['name']
        context['Nomatch'] = True
    else:
        context['Nomatch'] = False

    context['cell_list']=values
    context['query'] = query
    return render(request, 's.html', context) 

def index(request):
    query = request.GET.get('q')
    if query == None or query == '':
        return render(request, 'google5.html')

    if len(query) > 0:
        return HttpResponseRedirect('/search/?q=' + query)

def details(request):
    req = request.GET.get('req')
    query = request.GET.get('q')
    if req == None or req == '':
        return HttpResponse('[]')
    if query == None or query == '':
        return HttpResponse('[]')
    params = {'req':req,'q':query}
    try:
        json_dumped = requests.get('http://127.0.0.1:50000/details',params=params)
        return HttpResponse(json_dumped.text)
    except:
        return HttpResponse('[]')

def hots(request):
    order = request.GET.get('order')
    if order == None or order == "":
        order="comments"
    params = {'order':order}
    context = {}
    try:
        cell_list = requests.get('http://127.0.0.1:50000/hots',params=params)
        cell_list = cell_list.text
        cell_list = json.loads(cell_list)
        print len(cell_list)
        if len(cell_list) > 0:
            context['point'] = 1
            context['cell_list'] = cell_list
            print 'OK'
        return render(request, 'hots.html', context)
    except:
        return HttpResponse("None")
def news(request):
    def change_time(cell):
        cell['create_time'] = datetime.fromtimestamp(cell['create_time']).strftime('%Y-%m-%d %H:%M:%S')

    context = {}
    name = request.GET.get('name')
    if name == None or name == "":
        return HttpResponse('404')
    params = {'name':name}

    try:
        file = requests.get('http://127.0.0.1:50000/news',params=params).text
        json_file = json.loads(file)
        print json_file
        context['url'] = json_file['url']
        context['title'] = json_file['title']
        cell_list = json_file['content'].split('<br>')
        cell_list = [" ".join(cell_list)]
        context['cell_list'] = cell_list
        context['related'] = json_file['related']
        # print context['related']
        try:
            comment_list = []
            comments = json_file['comments']

            context['point'] = 1
            if len(comments) > 10000:
                comments = comments[0:10000]
            map(change_time,comments)
            context['comments'] = comments
        except:
            context['point'] = 0
                
    except:
        return HttpResponse('404')

    return render(request,'n.html',context)

def test(request):
    return render(request, 'test.html')



    