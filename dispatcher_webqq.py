# -*- coding: utf-8 -*-
import commom
import time
import json
import random
redis_conn = commom.redis_conn

def get_one_packet():
	packet = redis_conn.brpop("dispatcher:list")[1]
	return json.loads(packet)


def send_to_coarsefilter(message, extent_packet):
	extent_packet["process_by"] = "coarsefilter"
	packet = {
		"extent_packet": extent_packet,
		"message": message
	}
	json_packet = json.dumps(packet)
	redis_conn.lpush("coarse:filter:list", json_packet)


def send_to_spamfilter(message, extent_packet):
	extent_packet["process_by"] = "spamfilter"
	packet = {
		"extent_packet": extent_packet,
		"message": message
	}
	json_packet = json.dumps(packet)
	redis_conn.lpush("spam:filter:list", json_packet)



while True:
	conn = None
	try:
		conn = commom.get_mysql_conn()

		packet = get_one_packet()

		sub_packet = packet["sub_packet"]
		info_packet = packet["info_packet"]
		qqnum = packet["qqnum"]
		msg_uuid = str(packet["msg_uuid"])
		group_info_packet = packet.get("group_info_packet")

		poll_type = sub_packet["poll_type"]
		if poll_type == "group_message":
			_owner_qqnum = commom.convert_uincode_to_string(qqnum)
			_qq_group_num = group_info_packet["groupnum"]
			_qq_group_name = commom.convert_uincode_to_string(group_info_packet["name"])
			_qqnum = info_packet["qqnum"]
			_card = info_packet.get("card") or ""
			_card = commom.convert_uincode_to_string(_card)
			_nick_name = commom.convert_uincode_to_string(info_packet["nick"])
			_receive_time = sub_packet["value"]["time"]

			conn.query(
				"insert into group_chat_log (msg_uuid, owner_qqnum, qq_group_num, qq_group_name, qqnum, card, nick_name, content, receive_time, indate) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', now())" 
				% (msg_uuid,
					commom.escape_process(_owner_qqnum), 
					commom.escape_process(_qq_group_num), 
					commom.escape_process(_qq_group_name), 
					commom.escape_process(_qqnum), 
					commom.escape_process(_card), 
					commom.escape_process(_nick_name), 
					commom.escape_process(json.dumps(sub_packet)), 
					commom.escape_process(_receive_time)))

			conn.query("select last_insert_id() as last_insert_id")
			result = conn.store_result()
			last_insert_id = result.fetch_row(0, 1)[0]["last_insert_id"]


			extent_packet_commom_part = {
				"owner_qqnum": _owner_qqnum,
				"group_chat_log_kid": last_insert_id,
				"msg_uuid": msg_uuid
			}

			contents = sub_packet["value"]["content"]
			for content in contents:
				# if type(content) == type(u''):
				# 	content = commom.convert_uincode_to_string(content)
				if type(content) == type('') or type(content) == type(u''):
					if content != " ":
						if commom.convert_uincode_to_string(content).strip() == "@欢迎":
							gid = sub_packet["value"]["from_uin"]
							inner_packet = {
								"message":"欢迎各位老师参加我们的毕业答辩!",
								"gid":gid
							}
							commom.send_command(_owner_qqnum, "send_msg", redis_conn, inner_packet)
						elif commom.convert_uincode_to_string(content).strip() == "@笑话":
							mysql_conn = commom.get_mysql_conn()
							mysql_conn.query("select content from jokes")
							result_set = mysql_conn.store_result()
							table = result_set.fetch_row(0, 1)
							commom.release_mysql_conn(mysql_conn)
							
							idx = random.randint(0, len(table) - 1)
							send_content = table[idx]["content"]
							gid = sub_packet["value"]["from_uin"]
							inner_packet = {
								"message":send_content,
								"gid":gid
							}
							commom.send_command(_owner_qqnum, "send_msg", redis_conn, inner_packet)
						else:
							send_to_spamfilter(content, extent_packet_commom_part)
							send_to_coarsefilter(content, extent_packet_commom_part)

		if poll_type == "message":
			_owner_qqnum = commom.convert_uincode_to_string(qqnum)
			_qqnum = info_packet["qqnum"]
			_card = info_packet.get("card") or ""
			_card = commom.convert_uincode_to_string(_card)
			_nick_name = commom.convert_uincode_to_string(info_packet["nick"])
			_receive_time = sub_packet["value"]["time"]

			json_string = json.dumps(sub_packet)
			conn = commom.get_mysql_conn()
			conn.query(
				"insert into chat_log (msg_uuid, owner_qqnum, qqnum, card, nick_name, content, receive_time, indate) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', now())" 
				% (msg_uuid,
					commom.escape_process(_owner_qqnum), 
					commom.escape_process(_qqnum), 
					commom.escape_process(_card), 
					commom.escape_process(_nick_name), 
					commom.escape_process(json_string), 
					commom.escape_process(_receive_time)))

	except Exception, e:
		commom.report_error(commom.print_trace(e), "dispatcher_webqq")
	finally:
		commom.release_mysql_conn(conn)
