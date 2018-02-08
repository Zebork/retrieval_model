# -*- coding: utf-8 -*- 
import sys
import json
reload(sys)
sys.path.append("..")
sys.setdefaultencoding('utf-8')
import time
import db_connecter
class Search:
	def __init__(self):
		self.id = 0;
		self.newslist = [{'time':'2017.12.24 12:00','remarks':20,'title':'ChenChen Merry Christmas!','url':'http://y.baidu.com/song/282633'},
				{'time':'2017.12.23 12:00','remarks':30,'title':'ChenChen Merry Christmas!','url':'http://y.baidu.com/song/282633'},
				{'time':'2017.12.22 12:00','remarks':40,'title':'ChenChen Merry Christmas!','url':'http://y.baidu.com/song/282633'},
				{'time':'2017.12.21 12:00','remarks':50,'title':'ChenChen Merry Christmas!','url':'http://y.baidu.com/song/282633'},
				{'time':'2017.12.19 12:00','remarks':60,'title':'ChenChen Merry Christmas!','url':'http://y.baidu.com/song/282633'}]
	#返回热点新闻
	def QueryByRemarks(self):
		# newslist = list()
		return sorted(self.newslist,lambda x,y:cmp(y['remarks'],x['remarks']))

	#返回最新新闻
	def QueryByTime(self):
		# newslist = list()
		return sorted(self.newslist,lambda x,y:cmp(y['time'],x['time']))

