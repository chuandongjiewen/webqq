import control
import json
import time
import commom
redis_conn = commom.redis_conn


def add_user_qqnum(qqnum, uin):
	redis_key = "user:%s:%s" % (control.g_qqnum, uin)
	redis_value = commom.get_strdic_from_redis(redis_key, redis_conn)
	
	redis_value["qqnum"] = qqnum
	redis_value = json.dumps(redis_value)
	redis_conn.setex(redis_key, 172800, redis_value)

def add_group_qqnum(qqnum, uin):
	redis_key = "group:%s:%s" % (control.g_qqnum, uin)
	redis_value = commom.get_strdic_from_redis(redis_key, redis_conn)

	redis_value["groupnum"] = qqnum
	redis_value = json.dumps(redis_value)
	redis_conn.setex(redis_key, 172800, redis_value)

def set_friend_list(friend_list, qqnum):
	for item in friend_list:
		uin = item["uin"]

		redis_key = "user:%s:%s" % (qqnum, uin)
		old_redis_value = commom.get_strdic_from_redis(redis_key, redis_conn)
		item = commom.combine_dic(old_redis_value, item)
		redis_value = json.dumps(item)

		redis_conn.setex(redis_key, 172800, redis_value)

def set_card_list(card_list, qqnum):
	for item in card_list:
		uin = item["muin"]

		redis_key = "user:%s:%s" % (qqnum, uin)
		old_redis_value = commom.get_strdic_from_redis(redis_key, redis_conn)
		item = commom.combine_dic(old_redis_value, item)
		redis_value = json.dumps(item)

		redis_conn.setex(redis_key, 172800, redis_value)

def set_group_list(group_list, qqnum):
	for item in group_list:
		code = item["code"]

		redis_key = "group:%s:%s" % (qqnum, code)
		old_redis_value = commom.get_strdic_from_redis(redis_key, redis_conn)
		item = commom.combine_dic(old_redis_value, item)
		redis_value = json.dumps(item)

		redis_conn.setex(redis_key, 172800, redis_value)

def report_error_packet(code, _type, packet):
	t = time.time()
	json_packet = {"error_timestamp": t, "packet": packet, "code": code, "type": _type}
	json_packet = json.dumps(json_packet)

	return redis_conn.lpush("error:list:%s" % control.g_qqnum, json_packet)

def report_http_error_packet(code, user_data, cookies, res_headers, res_data, res_code, curl_code, exception_string):
	if type(res_data) == type(bytearray('')):
		res_data = "orignal bytearray"
	error_packet = {
		"user_data": user_data,
		"cookies": cookies,
		"response_headers": res_headers,
		"response_data": res_data,
		"response_code": res_code,
		"curl_code": curl_code,
		"exception_string": exception_string
	}

	return report_error_packet(code, "http", error_packet)

