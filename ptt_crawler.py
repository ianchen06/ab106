#!/usr/bin/env pyton
# coding: utf-8
from datetime import datetime

import requests
from bs4 import BeautifulSoup

HOST = "https://www.ptt.cc"

def crawl_list(url):
    # input: <String> list page url
    # output: <List> list of article urls
    headers = {
        'cookie': "over18=1"
    }
    res = requests.get(url, headers=headers)
    #print("[DEBUG] res page is %s"%(res.text))
    soup = BeautifulSoup(res.text, 'lxml')
    a_tags = soup.select("#main-container > div.r-list-container.action-bar-margin.bbs-screen > div > div.title > a")
    article_urls = [HOST + link['href'] for link in a_tags]
    return article_urls
	
def crawl_page(url):
    # input: <String> article page url
    # output: <Dictionary> article object
    print("[DEBUG] crawl_page at %s"%(url))
    article_dict = {}
    article_dict['url'] = url
    headers = {
        'cookie': "over18=1"
    }
    res = requests.get(url, headers=headers)
    #print("[DEBUG] res page is %s"%(res.text))
    soup = BeautifulSoup(res.text, 'lxml')
    meta_list = soup.select("#main-content > div > span.article-meta-value") # [kohanchen (kohanchen), Gossiping...]
    article_dict['author'] = meta_list[0].text
    article_dict['board'] = meta_list[1].text
    article_dict['title'] = meta_list[2].text
	
    dt = meta_list[3].text
	# 判斷是否需要補0
    if len(dt.split()[2]) < 2:
        dt_list = dt.split() # ['Tue', 'Mar', '2', '09:11:49', '2017']
        dt_list[2] = '0' + dt_list[2] # dt_list[2] = '0' + '2'
        dt = ' '.join(dt_list) # ['Tue', 'Mar', '02', '09:11:49', '2017']
	
    article_dict['dt'] = datetime.strptime(dt, '%a %b %d %H:%M:%S %Y')
    
    article_dict['ip'] = soup.select_one("#main-content").text.split("發信站: 批踢踢實業坊(ptt.cc), 來自: ")[1].split("\n※ 文章網址:")[0].strip()
    
    # 刪除不需要的elemets....
    for meta in meta_list:
        meta.extract()
    for meta in soup.select("#main-content > div > span.article-meta-tag"):
        meta.extract()
    for push in soup.select("div.push"):
        push.extract() 
    for push in soup.select("span.f2"):
        push.extract()

    article_dict['content'] = soup.select_one("#main-content").text.strip()
    
    return article_dict
	
def crawl_ptt(no_page):
	# 解決方法: 把不需要的element給刪掉(如作者，標題...)\
	# 開始組合八掛板列表頁URL
	res = requests.get(HOST + "/bbs/Gossiping/index.html")

	# Get last page
	headers = {
		'cookie': "over18=1"
	}
	res = requests.get(HOST + "/bbs/Gossiping/index.html", headers=headers)
	soup = BeautifulSoup(res.text, 'lxml')
	btn_list = soup.select("#action-bar-container > div > div.btn-group.btn-group-paging > a")
	last_page = int(btn_list[1]['href'].split("index")[1].split(".html")[0]) + 1
	print("[DEBUG] Last page is %s"%(last_page))
	
	URL_TEMPLATE = "/bbs/Gossiping/index{}.html"
	article_list = []
	for page in range(last_page, last_page - no_page, -1):
		print("[DEBUG] Crawling page %s"%(page))
		URL = HOST + URL_TEMPLATE.format(page)
		print("[DEBUG] Current page is %s"%(URL))
		for article in crawl_list(URL):
			try:
				article_dict = crawl_page(article)
			except Exception:
				pass
			article_list.append(article_dict)
	return article_list