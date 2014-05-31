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
import time
#import PyV8
import control
import uuid
import reporter
import os
import commom
import pprint
import encodings
import chardet

pp = pprint.PrettyPrinter()

#登录模块的错误号为100~199

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

print_trace = commom.print_trace

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

def _http_up(url, in_cookie = {}, post_data = None, referer = None, content_type = None):
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

	exec("uin = '%s'" % uin)
	if needs_vc == '1':
		return need_vc, "need verifycode", (verifycode, uin, cookies)
	return no_need_vc, "no need verifycode", (verifycode, uin, cookies)


def _get_token(html, cookies, qqnum):
	cookies["ptui_loginuin"] = qqnum
	
	
	url = re.findall('''http://.*\',''', html)[0].split("'")[0]
	b, html, code, cookies = _http_up(url, cookies)

	cookies.pop('superkey', None)
	cookies.pop('superuin', None)
	cookies.pop('supertoken', None)
	cookies.pop('ETK', None)


	ptwebqq = str(cookies["ptwebqq"])
	clientid = int(time.time() % 60000000)

	####GET TOKEN
	url = "http://d.web2.qq.com/channel/login2"
	#post_data = "r=%7B%22status%22%3A%22%22%2C%22ptwebqq%22%3A%22" + ptwebqq + "%22%2C%22passwd_sig%22%3A%22%22%2C%22clientid%22%3A%22" + str(clientid) + "%22%7D"
	post_data = urllib.urlencode({"r":json.dumps({"status":"online","ptwebqq":ptwebqq,"clientid":clientid,"passwd_sig":""})})
	b, html, code, cookies = _http_up(url, cookies, post_data, referer = "http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=3")
	pak = json.loads(html)
	psessionid = pak["result"]["psessionid"]
	vfwebqq = pak["result"]["vfwebqq"]

	##GET MSG_IDictxt = PyV8.JSContext()  
	t = time.time()
	t = int(t * 1000)
	t = (t - t % 1E3) / 1E3;
	t = int(t % 1E4 * 1E4);
	msg_id = t



	return psessionid, vfwebqq, ptwebqq, msg_id, clientid

def construct_get_friend_list(qqnum, vfwebqq, ptwebqq, cookies):
	url = "http://s.web2.qq.com/api/get_user_friends2"
	sending_data = urllib.urlencode({"r":json.dumps({"h":"hello","hash":_get_uin_ptwebqq_hash(qqnum, ptwebqq),"vfwebqq":vfwebqq})})
	req_headers = {}
	req_headers["Referer"] = "http://s.web2.qq.com/proxy.html?v=20110412001&callback=1&id=1"
	req_headers["Host"] = "s.web2.qq.com"

	user_data = {"key":"get_friend_list"}
	user_data = json.dumps(user_data)
	ret = (url, cookies, req_headers, control.DEF_POST, sending_data, user_data, 120)

	return ret


def process_get_friend_list(user_data, cookies, res_headers, res_data, res_code, curl_code, running_cnt):
	exception_string = None
	try:
		if int(res_code) == 200:
			_res_data = json.loads(res_data)
			retcode = _res_data["retcode"]
			if str(retcode) == '0':
				infos = _res_data["result"]["info"]
				friend_list = []
				for info in infos:
					uin = info["uin"]
					friend_list.append(info)

				reporter.set_friend_list(friend_list, control.g_qqnum)

				return
	except Exception, e:
		exception_string = commom.print_trace(e)
	reporter.report_http_error_packet(1001, user_data, cookies, res_headers, res_data, res_code, curl_code, exception_string)

def construct_get_group_list(cookies, vfwebqq):
	url = "http://s.web2.qq.com/api/get_group_name_list_mask2"
	sending_data = urllib.urlencode({"r":json.dumps({"vfwebqq":vfwebqq})})

	req_headers = {}
	req_headers["Referer"] = "http://s.web2.qq.com/proxy.html?v=20110412001&callback=1&id=1"
	req_headers["Host"] = "s.web2.qq.com"

	user_data = {"key":"get_group_list"}
	user_data = json.dumps(user_data)
	ret = (url, cookies, req_headers, control.DEF_POST, sending_data, user_data, 120)

	return ret

def process_get_group_list(user_data, cookies, res_headers, res_data, res_code, curl_code, running_cnt):
	exception_string = None
	try:
		if int(res_code) == 200:
			_res_data = json.loads(res_data)
			retcode = _res_data["retcode"]
			if str(retcode) == '0':
				gnamelist = _res_data["result"]["gnamelist"]
				group_list = []
				for gitem in gnamelist:
					gid = gitem["gid"]
					group_list.append(gitem)

				reporter.set_group_list(group_list, control.g_qqnum)
				return
	except Exception, e:
		exception_string = commom.print_trace(e)
	reporter.report_http_error_packet(1002, user_data, cookies, res_headers, res_data, res_code, curl_code, exception_string)



def login(qqnum, passwd, cookies, verifycode, uin):
	login_url = _get_login_url(qqnum, passwd, verifycode, uin)
	b, html, code, cookies = _http_up(login_url, cookies, referer = "http://ui.ptlogin2.qq.com/cgi-bin/login?daid=164&target=self&style=5&mibao_css=m_webqq&appid=1003903&enable_qlogin=0&no_verifyimg=1&s_url=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html&f_url=loginerroralert&strong_login=1&login_state=10&t=20131202001")
	if html.find("帐号或密码不正确") != -1:
		return login_account_passwd_error, "account or passwd error", (html, cookies)
	elif html.find("验证码不正确") != -1:
		return login_vc_error, "verifycode error", (html, cookies)
	elif html.find("登录成功") != -1:
		psessionid, vfwebqq, ptwebqq, msg_id, clientid = _get_token(html, cookies, qqnum)
		# friend_list = _get_friend_list(qqnum, vfwebqq, ptwebqq, cookies)
		# group_list = _get_group_list(cookies, vfwebqq)

		return login_succeed, "succeed", (html, cookies, msg_id, clientid, psessionid, vfwebqq, ptwebqq)
	else:
		return login_unknow_error, "unknow error", (html, cookies)


def construct_poll_pak(clientid, psessionid, cookies):
	url = "http://d.web2.qq.com/channel/poll2"
	referer = "http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=2"

	req_headers = {}
	req_headers["Referer"] = referer
	req_headers["Host"] = "d.web2.qq.com"
	r = {"clientid":clientid,"psessionid":psessionid,"key":0,"ids":[]}
	r = json.dumps(r)
	sending_data = {"r":str(r), "clientid":str(clientid), "psessionid":str(psessionid)}
	sending_data = urllib.urlencode(sending_data)
	user_data = {"key":"poll"}
	user_data = json.dumps(user_data)
	ret = (url, cookies, req_headers, control.DEF_POST, sending_data, user_data, 120)

	print "send a keep-alive packet"
	return ret

def get_image_url(value, psessionid):

	content = value["content"]
	for tx in content:
		if type(tx) != type([]):
			continue 
		if tx[0] == 'cface':
			pic_file = tx[1]
			pic_ser = pic_file["server"].split(':')
			pic_pid = psessionid[len(psessionid)-80:len(psessionid)]
			pic_url = "http://web2.qq.com/cgi-bin/get_group_pic?type=0&gid=" + str(value["group_code"]) + "&uin=" + str(value["send_uin"]) + "&rip=" + pic_ser[0] + "&rport=" + pic_ser[1] + "&fid=" + str(pic_file["file_id"]) + "&pic=" + pic_file["name"] + "&vfwebqq=" + pic_pid + "&t=" + str(value["time"])
			return pic_url


def construct_download_image(value, psessionid, file_name, cookies, msg_uuid):
	#cookies = {}
	url = get_image_url(value, psessionid)

	host = url.split("/")[2]
	req_headers = {}
	req_headers["Host"] = host

	user_data = {"key":"download_image", "file_name":file_name, "msg_uuid": msg_uuid}
	user_data = json.dumps(user_data)
	ret = (url, cookies, req_headers, control.DEF_GET, "", user_data, 120)

	print "send a pic download request"
	return ret

def construct_redirect_download_image(url, file_name, cookies, msg_uuid):
	host = url.split("/")[2]
	req_headers = {}
	req_headers["Host"] = host

	user_data = {"key":"redirect_download_image", "file_name":file_name, "msg_uuid": msg_uuid}
	user_data = json.dumps(user_data)
	ret = (url, cookies, req_headers, control.DEF_GET, "", user_data, 120)

	print "send a pic download request"
	return ret

def process_download_image(user_data, cookies, res_headers, res_data, res_code, curl_code, running_cnt):
	exception_string = None
	try:
		if int(res_code) == 302:
			print "relocation to get a downloaded pic"
			msg_uuid = user_data["msg_uuid"]
			file_name = user_data["file_name"]

			url = res_headers["Location"]

			pak = construct_redirect_download_image(url, file_name, control.g_cookies, msg_uuid)
			control.send_req(pak)
			return
		if int(res_code) == 200:
			file_name = user_data["file_name"]
			msg_uuid = user_data["msg_uuid"]
			file_dir = commom.sdbm_hash(file_name) % 1000
			file_dir = "./group_pic/%s" % file_dir
			file_path = "%s/%s" % (file_dir, file_name)
			print "get a downloaded pic"

			try:
				os.mkdir(file_dir)
			except:
				pass
			
			fp = open(file_path, "wb+")
			fp.write(res_data)
			fp.close()

			return_packet = {
				"type": "download_finished",
				"qqnum": control.g_qqnum,
				"file_path": file_path,
				"msg_uuid": msg_uuid,
				"file_name": file_name
			}

			json_packet = json.dumps(return_packet)
			commom.redis_conn.lpush("webqq:poll:list", json_packet)
			return
	except Exception, e:
		exception_string = commom.print_trace(e)
	reporter.report_http_error_packet(1003, user_data, cookies, res_headers, "PIC", res_code, curl_code, exception_string)



def process_poll_pak(user_data, cookies, res_headers, _res_data, res_code, curl_code, running_cnt):
	exception_string = None
	try:
		# res_data = control.bytearray_to_string(res_data)
		print curl_code
		print res_code
		if _res_data:
			res_data = json.loads(_res_data)
			ret_code = int(res_data["retcode"])

			if ret_code == 103 or ret_code == 121 or ret_code == 108:
				control.set_needs_login_flag()
				control._set_cmd(control.CMD_RENEW_SERVICE)
				reporter.report_http_error_packet(1000, user_data, cookies, res_headers, _res_data, res_code, curl_code, exception_string)
				return None
			if ret_code == 0:
				results = res_data["result"]
				return_packet = {
					"result": results,
					"type": "poll",
					"qqnum": control.g_qqnum
				}
				json_packet = json.dumps(return_packet)
				redis_conn = commom.redis_conn
				redis_conn.lpush("webqq:poll:list", json_packet)

		else:
			reporter.report_http_error_packet(1000, user_data, cookies, res_headers, _res_data, res_code, curl_code, exception_string)
	except Exception, e:
		exception_string = commom.print_trace(e)
		reporter.report_http_error_packet(1000, user_data, cookies, res_headers, _res_data, res_code, curl_code, exception_string)

	pak = construct_poll_pak(control.g_clientid, control.g_psessionid, control.g_cookies)
	control.send_req(pak)

def construct_send_msg(message, gid, cookies, msg_id, clientid, psessionid):
	content = [message, "", ["font",{"name":"宋体","size":"10","style":[0,0,0],"color":"000000"}]]
	content = json.dumps(content)
	post_data = {"r":json.dumps({"group_uin":gid,"content":content,"msg_id":msg_id,"clientid":clientid,"psessionid":psessionid})}
	sending_data = urllib.urlencode(post_data)
	url = "http://d.web2.qq.com/channel/send_qun_msg2"

	req_headers = {}
	req_headers["Referer"] = "http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=3"
	req_headers["Host"] = "d.web2.qq.com"
	req_headers["Content-Type"] = "application/x-www-form-urlencoded"

	user_data = {"key":"send_msg"}
	user_data = json.dumps(user_data)
	ret = (url, cookies, req_headers, control.DEF_POST, sending_data, user_data, 120)

	return ret
	
def process_send_msg(user_data, cookies, res_headers, _res_data, res_code, curl_code, running_cnt):
	print res_code
	print _res_data

def construct_get_real_qq_number(uin, cookies, vfwebqq, qqtype):
	url = "http://s.web2.qq.com/api/get_friend_uin2"
	sending_data = urllib.urlencode({"tuin":uin, "verifysession":'', "type":1, "code":'', "vfwebqq":vfwebqq, "t":str(int(time.time() * 1000))})

	req_headers = {}
	req_headers["Referer"] = "http://s.web2.qq.com/proxy.html?v=20110412001&callback=1&id=1"
	req_headers["Host"] = "s.web2.qq.com"

	user_data = {"key":"get_real_qq_number", "qqtype": qqtype, "uin": uin}
	user_data = json.dumps(user_data)
	ret = (url, cookies, req_headers, control.DEF_POST, sending_data, user_data, 120)

	return ret

def process_get_real_qq_number(user_data, cookies, res_headers, res_data, res_code, curl_code, running_cnt):
	exception_string = None
	try:
		if int(res_code) == 200:
			_res_data = json.loads(res_data)
			retcode = _res_data["retcode"]
			if str(retcode) == '0':
				qqnum = _res_data["result"]["account"]
				qqtype = user_data["qqtype"]
				uin = user_data["uin"]
				if qqtype == "user":
					reporter.add_user_qqnum(qqnum, uin)
				if qqtype == "group":
					reporter.add_group_qqnum(qqnum, uin)
				return
	except Exception, e:
		exception_string = commom.print_trace(e)
	reporter.report_http_error_packet(1004, user_data, cookies, res_headers, _res_data, res_code, curl_code, exception_string)


def construct_get_group_member(gcode, vfwebqq, cookies):
	url = "http://s.web2.qq.com/api/get_group_info_ext2"
	sending_data = urllib.urlencode({"gcode":gcode, "cb":'undefined', "vfwebqq":vfwebqq, "t":str(int(time.time() * 1000))})
	req_headers = {}
	req_headers["Referer"] = "http://s.web2.qq.com/proxy.html?v=20110412001&callback=1&id=1"
	req_headers["Host"] = "s.web2.qq.com"

	user_data = {"key":"get_group_member"}
	user_data = json.dumps(user_data)
	ret = (url, cookies, req_headers, control.DEF_POST, sending_data, user_data, 120)

	return ret

def process_get_group_member(user_data, cookies, res_headers, res_data, res_code, curl_code, running_cnt):
	exception_string = None
	try:
		if int(res_code) == 200:
			_res_data = json.loads(res_data)
			retcode = _res_data["retcode"]
			if str(retcode) == '0':
				card_list = _res_data["result"].get("cards")
				friend_list = _res_data["result"]["minfo"]
				reporter.set_friend_list(friend_list, control.g_qqnum)
				if card_list != None:
					reporter.set_card_list(card_list, control.g_qqnum)
				return
	except Exception, e:
		exception_string = commom.print_trace(e)
	reporter.report_http_error_packet(1005, user_data, cookies, res_headers, _res_data, res_code, curl_code, exception_string)

def get_friend_list(inner_packet):
	print "receive a get_friend_list command"
	pak = construct_get_friend_list(control.g_qqnum, control.g_vfwebqq, control.g_ptwebqq, control.g_cookies)
	control.send_req(pak)

def kill(inner_packet):
	print "receive a kill command"
	control._set_cmd(control.CMD_EXIT)

def get_group_list(inner_packet):
	print "receive a get_group_list command"
	pak = construct_get_group_list(control.g_cookies, control.g_vfwebqq)
	control.send_req(pak)

def download_image(inner_packet):
	print "receive a download_image command"
	value = inner_packet["value"]
	file_name = inner_packet["file_name"]
	msg_uuid = inner_packet["msg_uuid"]
	pak = construct_download_image(value, control.g_psessionid, file_name, control.g_cookies, msg_uuid)
	control.send_req(pak)


def get_user_qqnum(inner_packet):
	print "receive a get_user_qqnum command"
	uin = inner_packet["uin"]
	pak = construct_get_real_qq_number(uin, control.g_cookies, control.g_vfwebqq, "user")
	control.send_req(pak)

def get_group_num(inner_packet):
	print "receive a get_group_num command"
	uin = inner_packet["uin"]
	pak = construct_get_real_qq_number(uin, control.g_cookies, control.g_vfwebqq, "group")
	control.send_req(pak)

def get_group_member(inner_packet):
	print "receive a get_group_member command"
	uin = inner_packet["uin"]
	pak = construct_get_group_member(uin, control.g_vfwebqq, control.g_cookies)
	control.send_req(pak)

def send_msg(inner_packet):
	print "receive a send_msg command"
	message = inner_packet["message"]
	gid = inner_packet["gid"]
	control.g_msg_id += 1
	pak = construct_send_msg(message, gid, control.g_cookies, control.g_msg_id, control.g_clientid, control.g_psessionid)
	control.send_req(pak)

##CMD
control.registor_cmd_process("kill", kill)
control.registor_cmd_process("get_friend_list", get_friend_list)
control.registor_cmd_process("get_group_list", get_group_list)
control.registor_cmd_process("download_image", download_image)
control.registor_cmd_process("get_user_qqnum", get_user_qqnum)
control.registor_cmd_process("get_group_num", get_group_num)
control.registor_cmd_process("get_group_member", get_group_member)
control.registor_cmd_process("send_msg", send_msg)


##PROCESS
control.registor_res_process("poll", process_poll_pak)
control.registor_res_process("download_image", process_download_image)
control.registor_res_process("redirect_download_image", process_download_image)
control.registor_res_process("get_friend_list", process_get_friend_list)
control.registor_res_process("get_group_list", process_get_group_list)
control.registor_res_process("get_real_qq_number", process_get_real_qq_number)
control.registor_res_process("get_group_member", process_get_group_member)
control.registor_res_process("send_msg", process_send_msg)
