# -*- coding:UTF-8 -*-

import json
import jieba
import random
from jieba import analyse
from invert_class_compressed4 import Inverter

def sim_recomm(json_content):
	
	# similar news recommendation

	content = json.load(json_content)
	title = content['title'] 
	text = content['content'].replace('<br>',' ')

	try:
	    comments = content['comments']
	except:
	    comments = []

	tags = jieba.analyse.extract_tags(text, topK=5)

	sim_news = []

	#find the top-2 news that have the most similar topic(use title to represent the topic)
	# with the selected docment
	res = inverter.search_liner(title)
	if len(res) <= 1 :
		if len(res) == 1 :
			return res[0]
		else:
			return False

	#find 5 key words of the selected docment
	#randomly choose 3 of the key words and stitch them to a start new search
	#choose two of the return result
	#
	# loop twice
	#  
	x = 0
	while x < 2 :
		index = [random.randint(0,4) for _ in range(3)]
		comp_text = tags[index[0]]+','+tags[index[1]]+','+tags[index[2]]
		res = inverter.search_liner(comp_text)

		sim_news.append( res[0] )
		sim_news.append( res[1] )
		x = x + 1

	# return the result of the sim_news as an Array 
	return sim_news



if __name__ == '__main__':

	inverter = Inverter(mode=3,news_path='C:\Users\Administrator\Desktop\IR-work\ir\\tencent_cache')
	json_content = open('C:\Users\Administrator\Desktop\IR-work\\test.json')
	result = sim_recomm(json_content)

	print(result[0])
	print(result[1])
	print(result[2])
	print(result[3])
	print(result[4])
	print(result[5])