import commom
import time
import json
redis_conn = commom.redis_conn

_cache_control_table = {}

def fresh_query_key(qqnum, key, time):
	query_control_key = '__query__:__premession__:%s:%s' % (qqnum, key)
	redis_conn.setex(query_control_key, time, 1)

def get_query_premession(qqnum, key):
	query_control_key = '__query__:__premession__:%s:%s' % (qqnum, key)
	if redis_conn.get(query_control_key) == None:
		return True
	else:
		return False


def get_one_packet():
	packet = redis_conn.brpop("packetfixer:list")[1]
	return json.loads(packet)

while True:
	time.sleep(0.5)
	try:
		packet = get_one_packet()
		sub_packet = packet["sub_packet"]
		message_type = sub_packet["poll_type"]
		qqnum = packet["qqnum"]
		send_time = packet["send_time"]
		msg_uuid = packet["msg_uuid"]

		if time.time() - send_time > 600:
			conn = None
			try:
				conn = commom.get_mysql_conn()
				conn.query("insert into query_failed_packet (owner_qqnum, packet, indate) values ('%s', '%s', now())" % (qqnum, json.dumps(sub_packet)))
				commom.release_mysql_conn(conn)
			except:
				commom.release_mysql_conn(conn)
			continue

		if message_type == "message":
			value = sub_packet["value"]
			from_uin = value["from_uin"]

			user_packet = commom.lookup_user(qqnum, from_uin)
			if user_packet == None or user_packet.get("nick") == None:
				if get_query_premession(qqnum, "user"):
					fresh_query_key(qqnum, "user", 290)
					commom.send_command(qqnum, "get_friend_list", redis_conn)
				commom.pass_packet_to_packetfixer(qqnum, sub_packet, msg_uuid, send_time)
				continue
			elif user_packet.get("qqnum") == None:
				if get_query_premession(qqnum, from_uin):
					fresh_query_key(qqnum, from_uin, 290)
					commom.send_command(qqnum, "get_user_qqnum", redis_conn, {"uin":from_uin})
				commom.pass_packet_to_packetfixer(qqnum, sub_packet, msg_uuid, send_time)
				continue
			else:
				commom.pass_packet_to_dispatcher(qqnum, sub_packet, msg_uuid, user_packet)
				continue
				
		if message_type == "group_message":
			value = sub_packet["value"]
			group_code = value["group_code"]
			send_uin = value["send_uin"]

			contents = value["content"]

			group_packet = commom.lookup_group(qqnum, group_code)
			if group_packet == None or group_packet.get("name") == None:
				if get_query_premession(qqnum, "group"):
					fresh_query_key(qqnum, "group", 290)
					commom.send_command(qqnum, "get_group_list", redis_conn)
				commom.pass_packet_to_packetfixer(qqnum, sub_packet, msg_uuid, send_time)
				continue
			elif group_packet.get("groupnum") == None:
				if get_query_premession(qqnum, group_code):
					fresh_query_key(qqnum, group_code, 290)
					commom.send_command(qqnum, "get_group_num", redis_conn, {"uin":group_code})
				commom.pass_packet_to_packetfixer(qqnum, sub_packet, msg_uuid, send_time)
				continue

			user_packet = commom.lookup_user(qqnum, send_uin)
			if user_packet == None or user_packet.get("nick") == None:
				if get_query_premession(qqnum, "member"):
					fresh_query_key(qqnum, "member", 290)
					commom.send_command(qqnum, "get_group_member", redis_conn, {"uin":group_code})
				commom.pass_packet_to_packetfixer(qqnum, sub_packet, msg_uuid, send_time)
				continue
			elif user_packet.get("qqnum") == None:
				if get_query_premession(qqnum, send_uin):
					fresh_query_key(qqnum, send_uin, 290)
					commom.send_command(qqnum, "get_user_qqnum", redis_conn, {"uin":send_uin})
				commom.pass_packet_to_packetfixer(qqnum, sub_packet, msg_uuid, send_time)
				continue
			else:
				commom.pass_packet_to_dispatcher(qqnum, sub_packet, msg_uuid, user_packet, group_packet)
				continue


					
	except Exception, e:
		commom.report_error(commom.print_trace(e), "packetfixer")

