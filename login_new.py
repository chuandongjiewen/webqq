# -*- coding: utf-8 -*-
import urllib
import urllib2
import cookielib
import re
import hashlib
import sys
import json
import time
import datetime
import os
import mimetypes

#登录模块的错误号为100~199
qqnum = "1366810267"
passwd = "yh203808"

no_need_vc = 100
request_failed = 101
unknow_return_page = 102
need_vc = 103

get_vc_img_failed = 110
get_vc_img_succeed = 111

login_succeed = 120
login_account_passwd_error = 121
login_vc_error = 122
login_unknow_error = 123


class MYHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
	def redirect_request(self, req, fp, code, msg, headers, newurl):
		if req.headers.get("Host"):
			req.headers["Host"] = newurl.split("/")[2]
                return urllib2.HTTPRedirectHandler.redirect_request(self, req, fp, code, msg, headers, newurl)


def _qq_md5(var):
	var = hashlib.md5(var).hexdigest()
	return var.upper()

def _get_uin_ptwebqq_hash(uin, ptwebqq):
	b = uin
	i = ptwebqq
	b = int(b)
	a = {}
	s = 0
	for c in i:
	    if a.get(s % 4) == None:
	        a[s % 4] = 0
	    a[s % 4] ^= ord(c)
	    s += 1
	j = ["EC", "OK"]
	d = [0] * 4
	d[0] = b >> 24 & 255 ^ ord(j[0][0])
	d[1] = b >> 16 & 255 ^ ord(j[0][1])
	d[2] = b >> 8 & 255 ^ ord(j[1][0])
	d[3] = b & 255 ^ ord(j[1][1])
	j = {};
	for s in range(0, 8):
	    j[s] = a[s >> 1] if s % 2 == 0 else d[s >> 1];
	a = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"];
	d = "";
	for k,s in j.items():
	    d += a[s >> 4 & 15]
	    d += a[s & 15];
	return d


def _passwd_encode(passwd, verifycode, uin):
	M = passwd
	I = _qq_md5(M).decode("hex")
	H = _qq_md5(I + uin)
	G = _qq_md5(H + verifycode.upper())

	return G

def _get_login_url(qqnum, passwd, verifycode, uin):
	encoded_passwd = _passwd_encode(passwd, verifycode, uin)
	key = '''u=%s&p=%s&verifycode=%s''' % (qqnum, encoded_passwd, verifycode)
	login_url = '''http://ptlogin2.qq.com/login?''' + key + '''&webqq_type=10&remember_uin=1&login2qq=1&aid=1003903&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&h=1&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&mibao_css=m_webqq&t=1&g=1''' 
	return login_url

def _combine_cookies(old, new):
	for k, v in new.items():
		old[k] = v
	return old

def _http_up(url, in_cookie = {}, post_data = None, referer = None, content_type = None, host = None):
	if host == None:
		host = url.split("/")[2]
	cookies = cookielib.LWPCookieJar()
	handlers = [
	    urllib2.HTTPHandler(),
	    urllib2.HTTPSHandler(),
	    urllib2.HTTPCookieProcessor(cookies),
	    MYHTTPRedirectHandler
	    ]
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
	if referer:
		req.add_header("Referer", referer)
	#req.add_header('Accept-Encoding','gzip,deflate')
	req.add_header('Host', host)
	req.add_header('Connection','keep-alive')
	if content_type:
		req.add_header("Content-Type", content_type)
	if post_data:
		resp = urllib2.urlopen(req, post_data, timeout = 30)
	else:
		resp = urllib2.urlopen(req, timeout = 30)

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


def get_vc_img(qqnum, cookies):
	url = "http://captcha.qq.com/getimage?aid=1003903&uin=%s" % qqnum
	b, html, code, out_cookies = _http_up(url, cookies)
	if b == False:
		return get_vc_img_failed, "get verifycode image failed", (code, html)

	img = html
	return get_vc_img_succeed, "succeed", (img, out_cookies)

def check_need_vc(qqnum):
	b, html, code, cookies = _http_up("http://check.ptlogin2.qq.com/check?uin=%s&appid=1003903" % qqnum)

	if not b:
		return request_failed, "request failed", (code, html)	#请求出错
	
	ret = re.findall('''ptui_checkVC(.*)''', html)
	if not ret:
		return unknow_return_page, "unknow return page", (code, html)	#未知返回页面
	else:
		ret = ret[0]

	ret = ret.split("(")[1].split(")")[0].split(",")
	needs_vc = ret[0].split("'")[1]
	verifycode = ret[1].split("'")[1]
	uin = ret[2].split("'")[1]
	if needs_vc == '1':
		return need_vc, "need verifycode", (verifycode, uin, cookies)
	return no_need_vc, "no need verifycode", (verifycode, uin, cookies)

def login(qqnum, passwd, cookies, verifycode, uin):
	login_url = _get_login_url(qqnum, passwd, verifycode, uin)
	b, html, code, cookies = _http_up(login_url, cookies, referer = "http://ui.ptlogin2.qq.com/cgi-bin/login?daid=164&target=self&style=5&mibao_css=m_webqq&appid=1003903&enable_qlogin=0&no_verifyimg=1&s_url=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html&f_url=loginerroralert&strong_login=1&login_state=10&t=20131202001")
	if html.find("帐号或密码不正确") != -1:
		return login_account_passwd_error, "account or passwd error", (html, cookies)
	elif html.find("验证码不正确") != -1:
		return login_vc_error, "verifycode error", (html, cookies)
	elif html.find("登录成功") != -1:
		return login_succeed, "succeed", (html, cookies)
	else:
		return login_unknow_error, "unknow error", (html, cookies)

def login_succeed_process(items):
	cookies = items[1]
	cookies["ptui_loginuin"] = qqnum
	
	url = re.findall('''http://.*\',''', items[0])[0].split("'")[0]
	b, html, code, cookies = _http_up(url, cookies)

	cookies.pop('superkey', None)
	cookies.pop('superuin', None)
	cookies.pop('supertoken', None)
	cookies.pop('ETK', None)


	ptwebqq = str(cookies["ptwebqq"])
	clientid = 46779747

	####GET TOKEN
	url = "http://d.web2.qq.com/channel/login2"
	#post_data = "r=%7B%22status%22%3A%22%22%2C%22ptwebqq%22%3A%22" + ptwebqq + "%22%2C%22passwd_sig%22%3A%22%22%2C%22clientid%22%3A%22" + str(clientid) + "%22%7D"
	post_data = urllib.urlencode({"r":json.dumps({"status":"online","ptwebqq":ptwebqq,"clientid":clientid,"passwd_sig":""})})
	b, html, code, cookies = _http_up(url, cookies, post_data, referer = "http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=3")
	pak = json.loads(html)
	psessionid = pak["result"]["psessionid"]
	vfwebqq = pak["result"]["vfwebqq"]

	print psessionid, vfwebqq

	####GET FRIEND LIST
	url = "http://s.web2.qq.com/api/get_user_friends2"
	post_data = urllib.urlencode({"r":json.dumps({"h":"hello","hash":_get_uin_ptwebqq_hash(qqnum, ptwebqq),"vfwebqq":vfwebqq})})
	b, html, code, cookies = _http_up(url, cookies, post_data, referer = "http://s.web2.qq.com/proxy.html?v=20110412001&callback=1&id=1")

	pak = json.loads(html)
	fuin = pak["result"]["friends"][0]["uin"]


	##GET MSG_ID
	t = time.time()
	t = int(t * 1000)
	t = (t - t % 1E3) / 1E3;
	t = int(t % 1E4 * 1E4);
	msg_id = t


	####GET GROUP LIST
	url = "http://s.web2.qq.com/api/get_group_name_list_mask2"
	post_data = urllib.urlencode({"r":json.dumps({"vfwebqq":vfwebqq})})
	b, html, code, cookies = _http_up(url, cookies, post_data, referer = "http://s.web2.qq.com/proxy.html?v=20110412001&callback=1&id=1")
	pak = json.loads(html)
	gid = pak["result"]["gnamelist"][1]["gid"]
	group_code = pak["result"]["gnamelist"][1]["code"]

	r = {"clientid":clientid,"psessionid":psessionid,"key":0,"ids":[]}
	r = json.dumps(r)

	pic_sys = False
	pic_index = 1
	while True:
		bBBB = True
		try:
			# ###SEND MSG
			# msg_id += 1
			# content = ["我是虞华的测试机器人,请忽略此信息%s" % str(datetime.datetime.now()), "", ["font",{"name":"宋体","size":"10","style":[0,0,0],"color":"000000"}]]
			# content = json.dumps(content)
			# post_data = {"r":json.dumps({"to":fuin,"face":543,"content":content,"msg_id":msg_id,"clientid":clientid,"psessionid":psessionid})}
			# post_data = urllib.urlencode(post_data)
			# # post_data = "r=%7B%22to%22%3A" + str(fuin) + "%2C%22face%22%3A543%2C%22content%22%3A%22%5B%5C%22" + str(datetime.datetime.now()) +"%5C%22%2C%5C%22%5C%22%2C%5B%5C%22font%5C%22%2C%7B%5C%22name%5C%22%3A%5C%22%E5%AE%8B%E4%BD%93%5C%22%2C%5C%22size%5C%22%3A%5C%2210%5C%22%2C%5C%22style%5C%22%3A%5B0%2C0%2C0%5D%2C%5C%22color%5C%22%3A%5C%22000000%5C%22%7D%5D%5D%22%2C%22msg_id%22%3A" + str(msg_id) + "%2C%22clientid%22%3A%22" + str(clientid) + "%22%2C%22psessionid%22%3A%22" + str(psessionid) + "%22%7D"
			# # post_data += ("&clientid=" + str(clientid) + "&psessionid=" + str(psessionid))

			# url = "http://d.web2.qq.com/channel/send_buddy_msg2"
			# b, html, code, cookies = _http_up(url, cookies, post_data, referer = "http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=3", content_type="application/x-www-form-urlencoded")
			# print html

			# time.sleep(8)

			####SEND GROUP MSG
			msg_id += 1
			MSG = "我是虞华的测试机器人,请忽略此信息%s" % str(datetime.datetime.now())
			content = [MSG, "", ["font",{"name":"宋体","size":"10","style":[0,0,0],"color":"000000"}]]
			content = json.dumps(content)
			post_data = {"r":json.dumps({"group_uin":gid,"content":content,"msg_id":msg_id,"clientid":clientid,"psessionid":psessionid})}
			post_data = urllib.urlencode(post_data)
			url = "http://d.web2.qq.com/channel/send_qun_msg2"
			b, html, code, cookies = _http_up(url, cookies, post_data, referer = "http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=3", content_type="application/x-www-form-urlencoded")
			print "send group",html

			time.sleep(8)

			url = "http://d.web2.qq.com/channel/poll2"
			post_data = {"r":r, "clientid":clientid, "psessionid":psessionid}
			post_data = urllib.urlencode(post_data)

			b, html, code, cookies = _http_up(url, cookies, post_data, referer = "http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=2")
			
			getImages(html, psessionid)
		except:
			print "TIME OUT"
			bBBB = False
			pass
		if bBBB:
			time.sleep(8)
		# 这里是上传图片部分
		if not pic_sys:
			# filename现在暂时是要跟此py文件同一目录
			pic_name = upLoadImage(cookies, psessionid, pic_index, filename='21_1.jpg')
			pic_index += 1
			msg_id += 1
			t = str(int(time.time() * 1000))
			url = 'http://d.web2.qq.com/channel/get_gface_sig2?clientid=' + str(clientid) + '&psessionid=' + psessionid + '&t=' + t
			url += t
			# 这步只需做一次
			gface_key, gface_sig = getGfaceData(url, cookies)
			# 一回合君结束于此
			content = packGroupMsg(pic_name)
			# gid和group_code确定发向的q群
			post_data = {"r":json.dumps({"group_uin":gid,"content":content,"clientid":str(clientid),"psessionid":psessionid, "sig":gface_sig, "group_code":group_code, "key":gface_key}), 'clientid':clientid, 'psessionid':psessionid}
			post_data = urllib.urlencode(post_data)
			url = "http://d.web2.qq.com/channel/send_qun_msg2"
			sendImage(url, cookies, post_data)
			pic_sys = True
	print html

def getGfaceData(url, cookies):
	gface = _http_up(url, cookies, post_data=None, referer = "http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=2")
	gface = eval(gface[1])
	return gface['result']['gface_key'], gface['result']['gface_sig']

def sendImage(url, cookies, post_data):
	b, html, code, cookies = _http_up(url, cookies, post_data, referer = "http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=3", content_type="application/x-www-form-urlencoded")
	print "send group",html

def packGroupMsg(pic_name):
	MSG = "我是肥翔的测试机器人,请忽略此信息%s" % str(datetime.datetime.now())
	content = [MSG, ["cface","group", pic_name], ["font",{"name":"宋体","size":"10","style":[0,0,0],"color":"000000"}]]
	content = json.dumps(content)
	return content

# 上传图片，返回图片的名称，还需要做图片类型的判断
def upLoadImage(cookies, psessionid, fileid, filename):
	_boundary = '----------%s' % 'WebKitFormBoundarycaxgP3mQdLpTu5fe'
	_crlf = '\r\n'
	post_data = []
	pic_type = filename.split('.')
	pic_type = 'image' + pic_type[len(pic_type)-1]
	pic = open((getFilePath(filename)), 'rb').read()
	_post_pic_data = {'from':'control', 'f':'EQQ.Model.ChatMsg.callbackSendPicGroup', 'vfwebqq':(psessionid[len(psessionid)-80:len(psessionid)]).encode("utf8"), 'custom_face':filename, 'fileid':str(fileid)}
	for name in _post_pic_data:
		post_data.append('--' + _boundary)
		if name == 'custom_face':
			post_data.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (name, _post_pic_data[name]))
			post_data.append('Content-Type: %s' % pic_type)
			post_data.append('')
			post_data.append(pic)
		else:
			post_data.append('Content-Disposition: form-data; name="%s"' % name)
			post_data.append('')
			post_data.append(_post_pic_data[name])
	post_data.append('--' + _boundary + '--')
	post_data.append('')
	pic_data = _crlf.join(post_data)
	pic_time = int(time.time() * 1000)
	url = "http://up.web2.qq.com/cgi-bin/cface_upload?time=" + str(pic_time)
	# post_data = urllib.urlencode(post_data)
	b, html, code, cookies = _http_up(url, cookies, pic_data, referer = "http://web2.qq.com/webqq.html", content_type = ('multipart/form-data; boundary=%s' % _boundary))
	pic_name = html.split(':')
	pic_name = pic_name[2]
	pic_name = pic_name.split(' ')
	pic_name = pic_name[0]
	real_pic_name = pic_name[1:len(pic_name)]
	return real_pic_name

# 接收图片并且存储
def getImages(html, psessionid):
	html = json.loads(html)
	# html = eval(html)
	retcode = html["retcode"]
	if retcode != 0:
		return
	result = html["result"]
	for x in result:
		if x["poll_type"] != "group_message":
			continue
		value = x["value"]
		content = value["content"]
		for tx in content:
			if tx[0] == 'font':
				continue
			if tx[0] == 'cface':
				pic_file = tx[1]
				pic_ser = pic_file["server"].split(':')
				pic_pid = psessionid[len(psessionid)-80:len(psessionid)]
				pic_url = "http://web2.qq.com/cgi-bin/get_group_pic?type=0&gid=" + str(value["group_code"]) + "&uin=" + str(value["send_uin"]) + "&rip=" + pic_ser[0] + "&rport=" + pic_ser[1] + "&fid=" + str(pic_file["file_id"]) + "&pic=" + pic_file["name"] + "&vfwebqq=" + pic_pid + "&t=" + str(value["time"])
				print pic_url
				b, html, code, cookies = _http_up(pic_url)
				if b == False:
					print "can't get images!"
					return
				img = html
				fp = open("./" + pic_file["name"], "wb+")
				fp.write(img)
				fp.flush()
				fp.close()

def ReadFileAsContent(filename):
    try:
        with open(filename, 'rb') as f:
            filecontent = f.read()
    except Exception, e:
        print 'The Error Message in ReadFileAsContent(): ' + e.message 
        return ''
    return filecontent

# 获取 同一目录下 文件的 绝对路径
def getFilePath(filename):
    _localDir=os.path.dirname(__file__)
    _curpath=os.path.normpath(os.path.join(os.getcwd(),_localDir))
    curpath=_curpath
    realpath = os.path.join(curpath, filename)
    return realpath

#print _get_uin_ptwebqq_hash("1366810267", "3b8a227e9a5b436bc92bb537086b19e03f2dab78108d6d1554bedf579eb6f3e0")

# import pprint 
# pp = pprint.PrettyPrinter()
# pp.pprint(json.loads('''{"retcode":0,"result":{"friends":[{"flag":0,"uin":1218013384,"categories":0},{"flag":0,"uin":3973214140,"categories":0}],"marknames":[],"categories":[{"index":1,"sort":1,"name":"朋友"},{"index":2,"sort":2,"name":"家人"},{"index":3,"sort":3,"name":"同学"}],"vipinfo":[{"vip_level":0,"u":1218013384,"is_vip":0},{"vip_level":0,"u":3973214140,"is_vip":0}],"info":[{"face":546,"flag":8389122,"nick":"★音阶七..￡","uin":1218013384},{"face":570,"flag":8388608,"nick":"uuu","uin":3973214140}]}}'''))




# pak = {"tid":1244, "time_out":20, "host":"www.baidu.com", "data":"HHSUHUHUSHSUDHUSHUDHUSHDHUSHDHUHUSHUD"}
# print json.dumps(pak)




ret, msg, items = check_need_vc(qqnum)

cookies = items[2]
verifycode = items[0]
uin = items[1]
exec("uin = '%s'" % uin)


print uin
if ret == no_need_vc:
	ret, msg, items = login(qqnum, passwd, cookies, verifycode, uin)
	if ret == login_succeed:
		print "OK login succeed"
		login_succeed_process(items)
	else:
		print "error:", ret, msg, items
elif ret == need_vc:
	fp = open("./verifycode.jpeg", "wb+")
	ret, msg, items = get_vc_img(qqnum, cookies)
	if ret == get_vc_img_succeed:
		img = items[0]
		fp.write(img)
		fp.flush()
		fp.close()

		cookies = items[1]
		cookies.pop("confirmuin", None)

		print "please input verify code:"
		verifycode = sys.stdin.readline()
		verifycode = verifycode[0:-1]

		ret, msg, items = login(qqnum, passwd, cookies, verifycode, uin)
		if ret == login_succeed:
			print "OK login succeed"
			login_succeed_process(items)
		else:
			print "error:", ret, msg, items
	else:
		print "error:", ret, msg, items
else:
	print "error:", ret, msg, items

