import threading
import commom
redis_conn = commom.redis_conn
_CMD = 0

CMD_EXIT = 2
CMD_RENEW_SERVICE = 1

DEF_GET = 0
DEF_POST = 1

mutex_cmd = threading.Lock()

g_qqnum = None
g_cookies = None
g_friend_list = None
g_group_list = None
g_msg_id = None
g_psessionid = None
g_vfwebqq = None
g_ptwebqq = None
g_clientid = None


def _set_cmd(cmd):
	global _CMD
	mutex_cmd.acquire()
	_CMD = cmd
	mutex_cmd.release()

def _get_cmd():
	global _CMD
	mutex_cmd.acquire()
	cmd = _CMD
	_CMD = 0
	mutex_cmd.release()
	return cmd

g_logined = True
def needs_login():
	return g_logined

def set_logined_flag():
	global g_logined
	g_logined = False
	redis_conn.publish("webqq:status:%s" % g_qqnum, "loginok")

def set_needs_login_flag():
	global g_logined
	g_logined = True
	

REQUEST_LIST = []
m_process = {}

def send_req(pak):
	REQUEST_LIST.append(pak)

def get_one_req():
	pak = None
	try:
		pak = REQUEST_LIST.pop(0)
	except:
		pass
	return pak

#registor the process
def registor_res_process(key, pfunc):
	m_process[key] = pfunc

def get_res_process(key):
	return m_process.get(key)


m_cmd_precess = {}
#registor cmd process
def registor_cmd_process(key, pfunc):
	m_cmd_precess[key] = pfunc

def get_cmd_process(key):
	return m_cmd_precess.get(key)



# def bytearray_to_string(data):
# 	return data.decode("utf-8")
