import commom
import redis
import json
import time
import uuid
redis_conn = commom.redis_conn

#qqnum = "1366810267"

def get_one_packet():
	packet = redis_conn.brpop("webqq:poll:list")[1]

	return packet

def send_to_imagefilter(file_name, extent_packet):
	extent_packet["process_by"] = "imagefilter"
	packet = {
		"extent_packet": extent_packet,
		"file_name": file_name
	}
	json_packet = json.dumps(packet)
	redis_conn.lpush("image:filter:list", json_packet)


while True:
	try:
		json_packet = get_one_packet()
		# import MySQLdb
		# MySQLdb._mysql.

		#print json_packet
		webqq_packet = json.loads(json_packet)
		packet_type = webqq_packet["type"]
		qqnum = webqq_packet["qqnum"]
		if packet_type == "download_finished":
			file_path = webqq_packet["file_path"]
			file_name = webqq_packet["file_name"]
			msg_uuid = webqq_packet["msg_uuid"]
			extent_packet_commom_part = {
				"owner_qqnum": qqnum,
				"msg_uuid": msg_uuid
			}
			commom.set_pic_md5(file_name)
			send_to_imagefilter(file_path, extent_packet_commom_part)
			continue

		all_packet = webqq_packet["result"]

		# import pprint
		# pp = pprint.PrettyPrinter()
		# pp.pprint(all_packet)
		for sub_packet in all_packet:
			msg_uuid = str(uuid.uuid4())

			result = sub_packet

			message_type = result["poll_type"]

			if message_type == "sess_message":
				message_type = "message"
				result["poll_type"] = message_type
			if message_type == "message":
				value = result["value"]
				from_uin = value["from_uin"]

				user_packet = commom.lookup_user(qqnum, from_uin)
				if user_packet == None or user_packet.get("qqnum") == None or user_packet.get("nick") == None:
					commom.pass_packet_to_packetfixer(qqnum, sub_packet, msg_uuid, time.time())
					continue
				else:
					commom.pass_packet_to_dispatcher(qqnum, sub_packet, msg_uuid, user_packet)
					continue

			if message_type == "group_message":
				value = result["value"]
				group_code = value["group_code"]
				send_uin = value["send_uin"]

				contents = value["content"]
				
				for content in contents:
					if type(content) == type([]) and content[0] == 'cface':
						file_name = content[1]["name"]
						ret = commom.check_has_pic(file_name)
						if type(ret) != type(True):
							commom.report_error(commom.print_trace(ret), "receiver", qqnum)
						elif ret == False:
							inner_packet = {
								"value":value,
								"file_name":file_name,
								"msg_uuid": msg_uuid
							}
							commom.send_command(qqnum, "download_image", redis_conn, inner_packet)
						elif ret == True:
							extent_packet_commom_part = {
								"owner_qqnum": qqnum,
								"msg_uuid": msg_uuid
							}
							hash_id = commom.sdbm_hash(file_name) % 1000
							file_path = './group_pic/%s/%s' % (hash_id, file_name)
							send_to_imagefilter(file_path, extent_packet_commom_part)
						

				group_packet = commom.lookup_group(qqnum, group_code)
				if group_packet == None or group_packet.get("name") == None or group_packet.get("groupnum") == None:
					commom.pass_packet_to_packetfixer(qqnum, sub_packet, msg_uuid, time.time())
					continue

				user_packet = commom.lookup_user(qqnum, send_uin)
				if user_packet == None or user_packet.get("qqnum") == None or user_packet.get("nick") == None:
					commom.pass_packet_to_packetfixer(qqnum, sub_packet, msg_uuid, time.time())
					continue
				else:
					commom.pass_packet_to_dispatcher(qqnum, sub_packet, msg_uuid, user_packet, group_packet)
					continue
					
	except Exception, e:
		commom.report_error(commom.print_trace(e), "receiver")
