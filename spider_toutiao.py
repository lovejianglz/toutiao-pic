#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
1、Ajax请求：
method：GET
url：https://www.toutiao.com/search_content/
data：
	offset: 0
	format: json
	keyword: 街拍
	autoload: true
	count: 20
	cur_tab: 1
	from: search_tab
	pd: synthesis
2、从Ajax请求中获取title、article_url、gallary_image_count
3、从article_url中获取所有图片的url并下载
"""

import requests
from urllib.parse import urlencode
import re
import json
import os
import time
"""
1、获取搜索结果页面URL
2、进入获取图片列表的URL
3、新建以文章标题命名的文件夹
4、下载图片
"""
KEYWORD = "街拍"
COUNT = 100

def get_page(keyword, offset):
	"""
	获取搜索词为keyword，第offset条后的20条记录页面的url
	:param keyword 搜索关键字
	:param offset 返回第offset条记录后的20条搜索结果的页面的URL
	:return page_url_list
	"""
	url = "https://www.toutiao.com/search_content/?"
	headers = {
		"x-requested-with": "XMLHttpRequest",
		"content-type": "application/x-www-form-urlencoded",
		"accept": "application/json,text/javascript",
		"method": "GET",
		"user-agent": "Mozilla/5.0 (Windows NT 10.0;  WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari / 537.36",
		"authority": "www.toutiao.com"
	}
	data = {
		"format": "json",
		"autoload": "true",
		"count": "20",
		"cur_tab": "1",
		"from": "search_tab",
		"pd": "synthesis",
		"offset": offset,
		"keyword": keyword
	}
	query_data = urlencode(data, encoding="utf-8")
	response = requests.get(url=url+query_data, headers=headers)
	time.sleep(1)
	page_url_list = list()
	if response.status_code == 200:
		result = response.json()
		for i in result["data"]:
			if "article_url" in i:
				page_url_list.append("http://toutiao.com/"+i["item_source_url"])
		return page_url_list
	else:
		raise Exception("获取搜索结果出错")

def creat_file(pic_title):
	"""在当前目录下建立名为pic_title的文件夹"""
	file_list = os.listdir("./")
	if pic_title not in file_list:
		os.mkdir("./" + pic_title)

def download_pic(pic_title, pic_list):
	"""建立pic_title文件夹并下载pic_list中的图片到这个文件夹当中"""
	creat_file(pic_title)
	if pic_list:
		for i in pic_list:
			response = requests.get(i)
			time.sleep(1)
			if response.status_code == 200:
				img = response.content
				with open("./"+pic_title+"/"+i.split("/")[-1]+".jpg","wb") as f:
					f.write(img)
			else:
				print("获取{}图片失败".format(i))
	else:
		print(pic_title, "图片列表为空")

def get_pic_page(pic_page_url):
	headers = {
		"method": "GET",
		"user-agent": "Mozilla/5.0 (Windows NT 10.0;  WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari / 537.36",
		"authority": "www.toutiao.com",
	}
	page_text = None
	try:
		response = requests.get(pic_page_url, headers=headers)
		time.sleep(1)
		if response.status_code == 200:
			page_text = response.text
	except requests.RequestException:
		print("地址:{} 网络请求出错".format(pic_page_url))
	finally:
		return page_text

def get_pic_url_list_from_detail_page(page_text):
	pic_url_list = list()
	reg = re.compile(r"chineseTag: '([\u4e00-\u9fa5]+)',")
	print(page_text)
	try:
		search_result = re.search(reg,page_text).group(1)
	except AttributeError:
		print("网页类别正则表达式匹配错误")
	else:
		if search_result == "图片":
			pic_url_list = get_pic_url_list_from_pic_page(page_text)
		elif search_result == "摄影" or search_result == "其它":
			pic_url_list = get_pic_url_list_from_photography_page(page_text)
		else:
			print("此网页类型无法识别")
	return pic_url_list

def get_pic_url_list_from_pic_page(page_text):
	"""从图片分类的页面中提取URL"""
	pic_url_list = list()
	reg = re.compile(r"JSON.parse\(\"(.*?)\"\),")
	try:
		pic_json = re.search(reg,page_text).group(1)
	except AttributeError:
		print("正则匹配网页出错")
	else:
		for i in json.loads(pic_json.replace("\\",""))["sub_images"]:
			pic_url_list.append(i["url"])
	return pic_url_list

def get_pic_url_list_from_photography_page(page_text):
	"""从摄影分类的页面中提取URL"""
	reg = re.compile(r"(http://.*?/large/.*?)&quot")
	pic_url_list = re.findall(reg, page_text)
	return pic_url_list

def get_pic_title_from_pic_page(pic_page):
	reg = re.compile(r"title: '(.*?)',")
	search_result = re.search(reg, pic_page)
	if search_result:
		pic_title = search_result.group(1)
		return pic_title
	else:
		return "default"


# test
#print(get_pic_page("https://www.toutiao.com/a6602140390814384653/"))
#print(get_pic_url_list_from_detail_page(get_pic_page("https://www.toutiao.com/a6323345480202895617/")))
#
#exit(0)


if __name__ == "__main__":
	pic_page_url_list = list()
	for i in range(0,COUNT,20):
		pic_page_url_list.extend(get_page(KEYWORD, i))
	for i in pic_page_url_list:
		pic_page = get_pic_page(i)
		download_pic(get_pic_title_from_pic_page(pic_page),get_pic_url_list_from_detail_page(pic_page))