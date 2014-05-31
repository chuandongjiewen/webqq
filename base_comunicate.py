import sys, os
import qqprotocol
# import pprint
import time
import json
import signal
import control
import commom
redis_conn = commom.redis_conn

def signal_handler(signal, frame):
	print "receice a kill signal"
	control._set_cmd(control.CMD_EXIT)
signal.signal(signal.SIGINT, signal_handler)

def _get_cmd():
	return control._get_cmd()

print_trace = commom.print_trace


def http_request_packet(url, cookies, req_headers, req_type, sending_data, user_data, timeout):
	m = [url, cookies, req_headers, req_type, sending_data, user_data, timeout]

	return m


qqnum = None
passwd = None

def _call(cnt, arg_qqnum, arg_passwd):
	global qqnum
	global passwd

	try:
		current_path = os.path.dirname(__file__)
		if control.needs_login():
			qqnum = arg_qqnum.strip()
			control.g_qqnum = qqnum
			passwd = arg_passwd.strip()
			print "Start login"

			print "Checking if needs verify code"
			#check if needs verify code
			ret, msg, addtions = qqprotocol.check_need_vc(qqnum)

			verifycode = addtions[0]
			uin = addtions[1]
			cookies = addtions[2]
			
			if ret == qqprotocol.need_vc:
				cookies.pop("confirmuin", None)
				while True:
					#try change verify code until login succeed
					ret, msg, addtions = qqprotocol.get_vc_img(qqnum, cookies)

					if ret == qqprotocol.get_vc_img_failed:
						#critical:get verify code failed
						print msg
						print "CODE:", addtions[0]
						print "HTML:", addtions[1]
						control._set_cmd(control.CMD_EXIT)
						return None

					img = addtions[0]

					vc_path = os.path.join(current_path, "vc")
					vc_path = os.path.join(vc_path, "%s.jpg" % qqnum)
					fp = open(vc_path, "wb+")
					fp.write(img)
					fp.close()

					verifycode = raw_input("Please enter the verifycode:")
					redis_conn.publish("webqq:status:%s" % control.g_qqnum, "needsvc")
					#verifycode = redis_conn.brpop("webqq:vc:list:%s" % qqnum)[1]


					ret, msg, addtions = qqprotocol.login(qqnum, passwd, cookies, verifycode, uin)

					if ret == qqprotocol.login_succeed:
						control.g_cookies = addtions[1]
						control.g_msg_id = addtions[2]
						control.g_clientid = addtions[3]
						control.g_psessionid = addtions[4]
						control.g_vfwebqq = addtions[5]
						control.g_ptwebqq = addtions[6]

						
						control.set_logined_flag()

						pak = qqprotocol.construct_poll_pak(control.g_clientid, control.g_psessionid, control.g_cookies)
						return pak


					if ret == qqprotocol.login_unknow_error:
						print msg
						print "HTML:", addtions[0]
						print "COOKIES:", addtions[1]
						control._set_cmd(control.CMD_EXIT)
						return None

					if ret == qqprotocol.login_account_passwd_error:
						print msg
						control._set_cmd(control.CMD_EXIT)
						return None

					print "verify code error"
			else:
				print "No need verify code auto login"
				ret, msg, addtions = qqprotocol.login(qqnum, passwd, cookies, verifycode, uin)
				if ret != qqprotocol.login_succeed:
					#critical:login failed with correct verify code
					print msg
					print "HTML:", addtions[0]
					print "COOKIES:", addtions[1]
					control._set_cmd(control.CMD_EXIT)
					return None
				else:
					control.g_cookies = addtions[1]
					control.g_msg_id = addtions[2]
					control.g_clientid = addtions[3]
					control.g_psessionid = addtions[4]
					control.g_vfwebqq = addtions[5]
					control.g_ptwebqq = addtions[6]
					

					control.set_logined_flag()

					pak = qqprotocol.construct_poll_pak(control.g_clientid, control.g_psessionid, control.g_cookies)
					return pak
	except Exception, e:
		print print_trace(e)
		return None

	while True:
		try:
			cmd_pak = redis_conn.rpop("webqq:command:list:%s" % qqnum)
			if cmd_pak == None:
				break
			cmd_pak = json.loads(cmd_pak)
			cmd = cmd_pak["cmd"]
			inner_packet = cmd_pak["inner_packet"]
			pfunc = control.get_cmd_process(cmd)
			if pfunc == None:
				print "Key:%s doesn't match any command process" % cmd
				print "packet %s is abadoned" % cmd_pak
			else:
				pfunc(inner_packet)
		except Exception, e:
			print print_trace(e)


	pak = control.get_one_req()
	return pak

def _process_header(str_header):
	arrs = str_header.split("\n")
	res_headers = {}
	for item in arrs:
		try:
			item = item.split(":", 1)
			res_headers[item[0].strip()] = item[1].strip()
		except:
			pass
	return res_headers

def _back(user_data, cookies, res_headers, res_data, date_size, res_code, curl_code, running_cnt):
	try:
		res_headers = _process_header(res_headers)
		control.g_cookies = qqprotocol._combine_cookies(control.g_cookies, cookies)
	except Exception, e:
		print print_trace(e)

	key = None
	try:
		user_data = json.loads(user_data)
		key = user_data["key"]
	except Exception, e:
		print print_trace(e)

	pfunc = control.get_res_process(key)
	if pfunc == None:
		print "Key:%s doesn't match any process" % key
	else:
		try:
			try:
				content_type = res_headers.get("Content-Type")
				if content_type != None:
					content_type = content_type.lower()
					
					if content_type.find("utf-8") != -1:
						res_data = str(res_data)
					else:
						if content_type.find("text") != -1 or content_type.find("json") != -1:
							res_data = res_data.decode("utf-8")
			except:
				pass
			pfunc(user_data, control.g_cookies, res_headers, res_data, res_code, curl_code, running_cnt)
		except Exception, e:
			print print_trace(e)


	return None