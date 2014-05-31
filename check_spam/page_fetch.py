#encoding=utf-8
#import psyco
#psyco.full()
import urllib2
import cookielib
import re
import os
import time
import threading
import signal
import sys
from bs4 import BeautifulSoup

reHttp = re.compile(r'http://')
reMobile = re.compile(r'mobile')
reDouban = re.compile(r'douban')
urls = []
urls_hasFetch = {}
count = 1
lock_urls = threading.Lock()

def _combine_cookies(old, new):
	for k, v in new.items():
		old[k] = v
	return old


def page_fetch(url, in_cookie = {}, post_data = None, referer = None, content_type = None, proxy = None):
	host = url.split("/")[2]
	cookies = cookielib.LWPCookieJar()
	handlers = [
	    urllib2.HTTPHandler(),
	    urllib2.HTTPSHandler(),
	    urllib2.HTTPCookieProcessor(cookies)
	    ]

	if proxy != None:
		handlers.append(urllib2.ProxyHandler({'http':'%s:%s'%(str(proxy[0]),str(proxy[1]))}))
	opener = urllib2.build_opener(*handlers)
	all_cookie = ""
	for k,v in in_cookie.items():
		all_cookie += k + "=" + v + ";"
	if all_cookie:
		all_cookie = all_cookie[0:-1]
		opener.addheaders.append(('Cookie', all_cookie))

	urllib2.install_opener(opener)
		

	req = urllib2.Request(url)
	req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
	req.add_header('Accept-Language','zh-CN,zh;q=0.8')
	req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36')
	#req.add_header('User-Agent','curl/7.32.0')
	if referer:
		req.add_header("Referer", referer)
	#req.add_header('Accept-Encoding','gzip,deflate')
	req.add_header('Host', host)
	req.add_header('Connection','keep-alive')
	if content_type:
		req.add_header("Content-Type", content_type)
	if post_data:
		resp = urllib2.urlopen(req, post_data, timeout = 60)
	else:
		resp = urllib2.urlopen(req, timeout = 60)

	cookie_dic = {}
	for cookie in cookies:
		cookie_dic[cookie.name] = cookie.value

	cookie_dic = _combine_cookies(in_cookie, cookie_dic)

	html = resp.read()
	code = resp.code
	if code == 200:
		return True, html, code, cookie_dic
	else:
		return False, html, code, cookie_dic

def getFilePath(filename):
    _localDir=os.path.dirname(__file__)
    _curpath=os.path.normpath(os.path.join(os.getcwd(),_localDir))
    curpath=_curpath
    realpath = os.path.join(curpath, filename)
    return realpath

def getLinks(html, host):
	soup = BeautifulSoup(html)
	ankles = soup.find_all('a')
	for link in ankles:
		hype_link = link.get('href')
		if (hype_link != None or hype_link != "#") and hype_link != '':
			if reDouban.search(hype_link) == None:
				continue
			if not reHttp.match(hype_link):
		   		hype_link =  'http://' + host + hype_link
		   	lock_urls.acquire()
		   	urls.append(hype_link)
		   	lock_urls.release()

def do_in_thread(url, index, cookie):
	url = url.encode('utf8')
	host = url.split("/")[2]
	global count
	if reDouban.search(host) == None: 
		return
	retry = 0
	print "thread" + str(index) + "is running!"
	while retry < 3:
		try:
			ht = page_fetch(url, cookie)
		except:
			retry += 1
			continue
		if ht != None:
			fileh = open(getFilePath('result\\' + str(count) + '.txt'), 'w')
			fileh.write(ht[1])
			fileh.close()
			getLinks(ht[1], host)
			count += 1
			break
	print "thread" + str(index) + "is over!"

def wait_for_subcheck(list_th):
	thlen = len(list_th)
	_cnt = 0
	while True:
		for key,th in list_th.items():
			if not th.is_alive():
				_cnt += 1
		if _cnt >= thlen:
			yeild_subcheck(list_th)
			break
		_cnt = 0
		time.sleep(2)

def yeild_subcheck(list_th):
	for hid, th in list_th.items():
		if not th.is_alive():
			list_th.pop(hid, None)

def main(url):
	host = url.split("/")[2]
	resp = page_fetch(url)
	soup = BeautifulSoup(resp[1])
	links = soup.find_all('a')
	list_th = {}
	th_cnt = 0
	_max_th = 4
	rc = 0
	cookie = resp[3]
	for link in links:
		hype_link = link.get("href")
		if (hype_link != None or hype_link != "#") and hype_link != '':	
		   	if not reHttp.match(hype_link):
		   		hype_link =  'http://' + host + hype_link
		   	urls.append(hype_link)
	while rc < 3:
		lock_urls.acquire()
		try:
			one_link = urls.pop(0)
		except:
			lock_urls.release()
			time.sleep(4)
			continue
		lock_urls.release()
		if one_link in urls_hasFetch:
			continue
		urls_hasFetch[one_link] = True
		th = threading.Thread(target = do_in_thread, args = (one_link, th_cnt, cookie))
		th.start()
		list_th[th_cnt] = th
		th_cnt += 1
		tl = len(list_th)
		if tl >=_max_th:
			wait_for_subcheck(list_th)
			time.sleep(6)
		lock_urls.acquire()
		les = len(urls)
		lock_urls.release()
		print les
		if les == 0:
			rc += 1
			time.sleep(4)
	# for i in range(200):
	# 	hype_link = urls[i].encode('utf8')
	# 	print(hype_link)
	# 	try:
	# 		ht = page_fetch(hype_link)
	# 	except:
	# 		print 'not found!' + str(i)
	# 		continue
	# 	fileh = open(getFilePath('result\\' + str(i) + '.txt'), 'w')
	# 	fileh.write(ht[1])
	# 	fileh.close()


main('http://www.douban.com/')
# test_result = page_fetch('http://www.douban.com/')
# test_result = BeautifulSoup(test_result[1])
# link_file_path = getFilePath('links.txt')
# link_file = open(link_file_path, 'w')
# # print test_result[1].decode('utf8')
# links = test_result.find_all("a")
# for link in links:
#    hype_link = link.get("href")
#    if (hype_link != None or hype_link != "#") and hype_link != '':
# 	link_file.write(hype_link.encode('gb2312'))
# 	link_file.write('\n')
# 	#print hype_link
# link_file.close()
# movie_link = links[44].get("href")
# movie = page_fetch(movie_link.encode('gb2312'))
# print movie[1]
# print movie_link.encode('gb2312')