import json
import traceback, sys, os
import address
import time
import redis
import MySQLdb
import _mysql_exceptions
import hashlib
def get_mysql_conn():
	conn = MySQLdb.Connect(
                    user = address.mysql_address["user"],
                    passwd = address.mysql_address["passwd"],
                    db = address.mysql_address["db"],
                    host = address.mysql_address["host"],
                    port = address.mysql_address["port"]
                    )
	conn.query("SET NAMES utf8")
	return conn

def release_mysql_conn(conn):
	if conn != None:
		conn.close()
redis_conn = redis.StrictRedis(host=address.redis_address["host"], port=address.redis_address["port"], db=address.redis_address["db"])

def sdbm_hash(string):
	return_value = 0
	for c in string:
		return_value = ord(c) + (return_value << 6) + (return_value << 16) - return_value;
	return_value = return_value & 0x7FFFFFFF

	return return_value

def send_command(qqnum, cmd, redis_conn = redis_conn, inner_packet = {}):
	pak = {}
	pak["cmd"] = cmd
	pak["inner_packet"] = inner_packet

	pak = json.dumps(pak)
	redis_conn.lpush("webqq:command:list:%s" % qqnum, pak)


def lookup_user(qqnum, uin, redis_conn = redis_conn):
	redis_key = "user:%s:%s" % (qqnum, uin)
	redis_value = redis_conn.get(redis_key)
	if redis_value == None:
		return None
	return json.loads(redis_value)

def lookup_group(qqnum, uin, redis_conn = redis_conn):
	redis_key = "group:%s:%s" % (qqnum, uin)
	redis_value = redis_conn.get(redis_key)
	if redis_value == None:
		return None
	return json.loads(redis_value)

def print_trace(e, addtion = None):
    err = str(e)
    trace_back = traceback.format_exc();
    # typ, _, _ = sys.exc_info()    

    exc_str = "Type:%s\n\n%s\nDescript:\n%s" % (type(e), trace_back, err)
    if addtion != None:
        exc_str += ("\n\nAddtion:\n" + addtion)
    return exc_str

def get_current_timeid():
	return int(time.time() / 600)

def report_error(descript, host, qqnum = "all"):
	mysql = get_mysql_conn()
	descript = mysql.escape_string(descript)
	qqnum = mysql.escape_string(qqnum)
	mysql.query("insert into merror (host,qqnum,descript,indate) values ('%s','%s','%s',now())" % (host, qqnum, descript))
	release_mysql_conn(mysql)

def combine_dic(old_dic, new_dic):
	for k, v in new_dic.items():
		old_dic[k] = v
	return old_dic

def get_strdic_from_redis(redis_key, redis_conn):
	redis_value = redis_conn.get(redis_key)
	if redis_value == None:
		return {}
	else:
		return json.loads(redis_value)

def check_has_pic(pic_name):
	m = hashlib.md5(pic_name)
	pic_name_md5 = str(m.hexdigest())

	try:
		mysql = get_mysql_conn()
		mysql.query("select * from picture_name_md5 where pic_name_md5 = '%s'" % pic_name_md5)
		result = mysql.store_result()
		table = result.fetch_row(1, 0)
		if len(table) >= 1:
			return True
	except _mysql_exceptions.IntegrityError, e:
			return e
	except Exception, e:
		return True
	finally:
		release_mysql_conn(mysql)
	return False

def set_pic_md5(pic_name):
	m = hashlib.md5(pic_name)
	pic_name_md5 = str(m.hexdigest())

	try:
		mysql = get_mysql_conn()
		mysql.query("insert into picture_name_md5 (pic_name_md5,indate) values ('%s',now())" % pic_name_md5)
	except _mysql_exceptions.IntegrityError, e:
		if e[0] == 1062:
			return True
		else:
			return e
	except Exception, e:
		return e
	finally:
		release_mysql_conn(mysql)
	return False

def pass_packet_to_packetfixer(qqnum, sub_packet, msg_uuid, send_time):
	packet = {
		"qqnum":qqnum,
		"sub_packet":sub_packet,
		"send_time": send_time,
		"msg_uuid": msg_uuid
	}
	json_packet = json.dumps(packet)

	list_name = "packetfixer:list"
	redis_conn.lpush(list_name, json_packet)

def pass_packet_to_dispatcher(qqnum, sub_packet, msg_uuid, info_packet, group_info_packet = None):
	packet = {
		"qqnum": qqnum,
		"sub_packet": sub_packet,
		"info_packet": info_packet,
		"msg_uuid": msg_uuid
	}
	if group_info_packet != None:
		packet["group_info_packet"] = group_info_packet
	json_packet = json.dumps(packet)

	list_name = "dispatcher:list"
	redis_conn.lpush(list_name, json_packet)

def escape_process(string):
	string = str(string)
	return MySQLdb._mysql.escape_string(string)
	#return string

def convert_uincode_to_string(_unicode):
	if type(_unicode) == type(u'unicode'):
		_unicode = _unicode.encode("utf-8", 'ignore')
		return escape_process(_unicode)
