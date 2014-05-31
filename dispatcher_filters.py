# -*- coding: utf-8 -*-
import commom
import json
import time
redis_conn = commom.redis_conn

def get_one_packet():
	json_packet = redis_conn.brpop("filters:result:list")[1]

	packet = json.loads(json_packet)

	return packet

def get_old_tag(row):
	tag = row["tag"]
	if tag == "None":
		return {}
	return json.loads(tag)

def set_new_tag(msg_uuid, tag):
	json_tag = json.dumps(tag)
	mysql_conn = commom.get_mysql_conn()
	json_tag = commom.escape_process(json_tag)

	mysql_conn.query("update group_chat_log set tag = '%s' where msg_uuid = '%s'" % (json_tag, msg_uuid))
	commom.release_mysql_conn(mysql_conn)

def get_group_chat_log_by_msg_uuid(msg_uuid):
	mysql_conn = commom.get_mysql_conn()
	mysql_conn.query("select * from group_chat_log where msg_uuid = '%s'" % msg_uuid)
	result = mysql_conn.store_result()
	row = result.fetch_row(0, 1)[0]
	commom.release_mysql_conn(mysql_conn)

	return row


while True:
	try:
		packet = get_one_packet()

		extent_packet = packet["extent_packet"]
		process_by = extent_packet["process_by"]
		msg_uuid = extent_packet["msg_uuid"]
		owner_qqnum = extent_packet["owner_qqnum"]
		if process_by == "imagefilter":
			row = get_group_chat_log_by_msg_uuid(msg_uuid)
			tag = get_old_tag(row)
			skin_area = packet["skin_area"]
			tag["skin_area"] = skin_area
			set_new_tag(msg_uuid, tag)

			if redis_conn.get("open_pornpic") == "false":
				continue
			if skin_area > 0.3:
				nick = row["nick_name"]
				sender_qqnum = row["qqnum"]
				content = json.loads(row["content"])

				gid = content["value"]["from_uin"]

				receive_time = row["receive_time"]
				receive_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(receive_time))
				inner_packet = {
					"message":"<警告>%s(%s)在%s发送的内容疑似含有色情图片." % (nick, sender_qqnum, receive_time),
					"gid": gid
				}
				commom.send_command(owner_qqnum, "send_msg", redis_conn, inner_packet)

		elif process_by == "coarsefilter":
			
			row = get_group_chat_log_by_msg_uuid(msg_uuid)
			tag = get_old_tag(row)
			has_coarse = packet["has_coarse"]
			tag["has_coarse"] = packet["has_coarse"]
			set_new_tag(msg_uuid, tag)

			if redis_conn.get("open_coarse") == "false":
				continue
			if has_coarse:
				nick = row["nick_name"]
				sender_qqnum = row["qqnum"]
				content = json.loads(row["content"])
				
				gid = content["value"]["from_uin"]
				print gid
				receive_time = row["receive_time"]
				receive_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(receive_time))
				inner_packet = {
					"message":"<警告>%s(%s)在%s发送的内容疑似含有色情暴力用语." % (nick, sender_qqnum, receive_time),
					"gid": gid
				}
				commom.send_command(owner_qqnum, "send_msg", redis_conn, inner_packet)
		elif process_by == "spamfilter":
			row = get_group_chat_log_by_msg_uuid(msg_uuid)
			tag = get_old_tag(row)
			word_fin = packet["word_fin"]
			word_sub = packet["word_sub"]
			tag["word_fin"] = word_fin
			tag["word_sub"] = word_sub
			set_new_tag(msg_uuid, tag)

			if redis_conn.get("open_advertisement") == "false":
				continue
			if word_fin > word_sub:
				nick = row["nick_name"]
				sender_qqnum = row["qqnum"]
				content = json.loads(row["content"])
				
				gid = content["value"]["from_uin"]
				receive_time = row["receive_time"]
				receive_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(receive_time))
				inner_packet = {
					"message":"<警告>%s(%s)在%s发送的内容疑似含有广告用语." % (nick, sender_qqnum, receive_time),
					"gid": gid
				}
				commom.send_command(owner_qqnum, "send_msg", redis_conn, inner_packet)

		# elif process_by == "":
		# 	pass
		else:
			commom.report_error("Unknow processer", "dispatcher_filters")
	except Exception, e:
		commom.report_error(commom.print_trace(e), "dispatcher_filters")
		

	
	