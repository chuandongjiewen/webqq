import commom
import json
import datetime
import time
redis_conn = commom.redis_conn
datetime_type = type(datetime.datetime.now())

def get_one_packet():
	json_packet = redis_conn.brpop("queryer:list")[1]
	return json.loads(json_packet)


def return_packet(extent_packet, listid, result):
	try:
		for idx,row in enumerate(result):
			for k,item in row.items():
				if type(item) == datetime_type:
					result[idx][k] = str(item)
	except:
		pass

	return_packet = {
		"extent_packet": extent_packet,
		"result": result
	}

	json_packet = json.dumps(return_packet)
	redis_conn.lpush("queryer:result:list:%s" % listid, json_packet)

def query_chat_log_by_receive_time_less(inner_packet, mysql_conn):
	
	receive_time = inner_packet.get("receive_time")
	owner_qqnum = inner_packet["owner_qqnum"]
	count = inner_packet["count"]
	
	if receive_time == None:
		mysql_conn.query("select * from chat_log where owner_qqnum = '%s' order by receive_time desc limit %s" % (owner_qqnum, count))
	else:
		mysql_conn.query("select * from chat_log where owner_qqnum = '%s' and receive_time < %s order by receive_time desc limit %s" % (owner_qqnum, receive_time, count))

	result_set = mysql_conn.store_result()
	result = result_set.fetch_row(0, 1)

	return result

def query_chat_log_by_receive_time_greater(inner_packet, mysql_conn):
	receive_time = inner_packet["receive_time"]
	owner_qqnum = inner_packet["owner_qqnum"]
	count = inner_packet.get("count")

	if count == None:
		count = 1000000000
	
	mysql_conn.query("select * from group_chat_log where owner_qqnum = '%s' and receive_time > %s order by receive_time asc limit %s" % (owner_qqnum, receive_time, count))

	result_set = mysql_conn.store_result()
	result = result_set.fetch_row(0, 1)
	
	return result


def query_group_chat_log_by_receive_time_less(inner_packet, mysql_conn):
	receive_time = inner_packet.get("receive_time")
	owner_qqnum = inner_packet["owner_qqnum"]
	qq_group_num = inner_packet["qq_group_num"]
	count = inner_packet["count"]
	
	if receive_time == None:
		mysql_conn.query("select * from group_chat_log where owner_qqnum = '%s' and qq_group_num = '%s' order by receive_time desc limit %s" % (owner_qqnum, qq_group_num, count))
		print "select * from group_chat_log where owner_qqnum = '%s' and qq_group_num = '%s' order by receive_time desc limit %s" % (owner_qqnum, qq_group_num, count)
	else:
		mysql_conn.query("select * from group_chat_log where owner_qqnum = '%s' and qq_group_num = '%s' and receive_time < %s order by receive_time desc limit %s" % (owner_qqnum, qq_group_num, receive_time, count))
		print "select * from group_chat_log where owner_qqnum = '%s' and qq_group_num = '%s' and receive_time < %s order by receive_time desc limit %s" % (owner_qqnum, qq_group_num, receive_time, count)

	result_set = mysql_conn.store_result()
	result = result_set.fetch_row(0, 1)
	
	return result

def query_group_chat_log_by_receive_time_greater(inner_packet, mysql_conn):
	receive_time = inner_packet["receive_time"]
	owner_qqnum = inner_packet["owner_qqnum"]
	qq_group_num = inner_packet["qq_group_num"]
	count = inner_packet.get("count")

	if count == None:
		count = 1000000000
	
	mysql_conn.query("select * from group_chat_log where owner_qqnum = '%s' and qq_group_num = '%s' and receive_time > %s order by receive_time asc limit %s" % (owner_qqnum, qq_group_num, receive_time, count))

	result_set = mysql_conn.store_result()
	result = result_set.fetch_row(0, 1)

	print "select * from group_chat_log where owner_qqnum = '%s' and qq_group_num = '%s' and receive_time > %s order by receive_time asc limit %s" % (owner_qqnum, qq_group_num, receive_time, count)
	print result
	return result

def query_daily_pornpic_rank(inner_packet, mysql_conn):
	owner_qqnum = inner_packet["owner_qqnum"]
	qq_group_num = inner_packet["qq_group_num"]
	t = int(time.time() - 86400)
	mysql_conn.query("select * from group_chat_log where qq_group_num = '%s' and owner_qqnum = '%s' and receive_time >= %s" % (qq_group_num, owner_qqnum, t))
	print "select * from group_chat_log where qq_group_num = '%s' and owner_qqnum = '%s' and receive_time >= %s" % (qq_group_num, owner_qqnum, t)

	result_set = mysql_conn.store_result()
	result = result_set.fetch_row(0, 1)

	res = {}
	for item in result:
		try:
			tag = item["tag"]
			tag = json.loads(tag)
			skin_area = tag["skin_area"]
			if skin_area < 0.3:
				continue
			if res.get(item["qqnum"]) == None:
				res[item["qqnum"]] = {"count":0, "nick":item["nick_name"]}
			res[item["qqnum"]]["count"] += 1
		except:
			pass

	return res


def query_daily_coarse_rank(inner_packet, mysql_conn):
	owner_qqnum = inner_packet["owner_qqnum"]
	qq_group_num = inner_packet["qq_group_num"]
	t = int(time.time() - 86400)
	mysql_conn.query("select * from group_chat_log where qq_group_num = '%s' and owner_qqnum = '%s' and receive_time >= %s" % (qq_group_num, owner_qqnum, t))
	print "select * from group_chat_log where qq_group_num = '%s' and owner_qqnum = '%s' and receive_time >= %s" % (qq_group_num, owner_qqnum, t)

	result_set = mysql_conn.store_result()
	result = result_set.fetch_row(0, 1)

	res = {}
	for item in result:
		try:
			tag = item["tag"]
			tag = json.loads(tag)
			has_coarse = tag["has_coarse"]
			if not has_coarse:
				continue
			if res.get(item["qqnum"]) == None:
				res[item["qqnum"]] = {"count":0, "nick":item["nick_name"]}
			res[item["qqnum"]]["count"] += 1
		except:
			pass

	return res

def query_daily_advertisement_rank(inner_packet, mysql_conn):
	owner_qqnum = inner_packet["owner_qqnum"]
	qq_group_num = inner_packet["qq_group_num"]
	t = int(time.time() - 86400)
	mysql_conn.query("select * from group_chat_log where qq_group_num = '%s' and owner_qqnum = '%s' and receive_time >= %s" % (qq_group_num, owner_qqnum, t))
	print "select * from group_chat_log where qq_group_num = '%s' and owner_qqnum = '%s' and receive_time >= %s" % (qq_group_num, owner_qqnum, t)

	result_set = mysql_conn.store_result()
	result = result_set.fetch_row(0, 1)

	res = {}
	for item in result:
		try:
			tag = item["tag"]
			tag = json.loads(tag)
			word_fin = tag["word_fin"]
			word_sub = tag["word_sub"]
			if word_fin > word_sub:
				continue
			if res.get(item["qqnum"]) == None:
				res[item["qqnum"]] = {"count":0, "nick":item["nick_name"]}
			res[item["qqnum"]]["count"] += 1
		except:
			pass

	return res

call_map = {
	"query_chat_log_by_receive_time_less": query_chat_log_by_receive_time_less,
	"query_chat_log_by_receive_time_greater": query_chat_log_by_receive_time_greater,
	"query_group_chat_log_by_receive_time_less": query_group_chat_log_by_receive_time_less,
	"query_group_chat_log_by_receive_time_greater": query_group_chat_log_by_receive_time_greater,
	"query_daily_pornpic_rank": query_daily_pornpic_rank,
	"query_daily_coarse_rank": query_daily_coarse_rank,
	"query_daily_advertisement_rank": query_daily_advertisement_rank

}
# conn = commom.get_mysql_conn()
# import pprint
# pp = pprint.PrettyPrinter()
# inner_packet = {}
# inner_packet["qq_group_num"] = "376024301"
# inner_packet["owner_qqnum"] = "2330453668"
# pp.pprint(query_daily_pornpic_rank(inner_packet, conn))

while True:
	conn = None
	try:
		conn = commom.get_mysql_conn()
		packet = get_one_packet()

		interface = packet["interface"]
		print interface
		
		inner_packet = packet["inner_packet"]
		extent_packet = packet["extent_packet"]
		listid = packet["listid"]
		pfunc = call_map[interface]
		result = pfunc(inner_packet, conn)

		return_packet(extent_packet, listid, result)
	except Exception, e:
		commom.report_error(commom.print_trace(e), "queryer")

