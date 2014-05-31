#!/usr/bin/python
#encoding=utf-8
import os
import smallseg

def get_utf8_len(uchar):
	c = ord(uchar)
	if (c & 0x80) == 0:
		return 1

	r = 0x40
	l = 1
	while (r & c) != 0:
		r = r >> 1
		l += 1
	return l

		
def get_utf8_code(ustr, l = None):
	if l == None:
		l = get_utf8_len(ustr[0])
	if l == 1:
		return ord(ustr[0])
	else:
		f = 0x0ff >> l
		f = ord(ustr[0]) & f
		r = 0x3f
		for i in range(1, l):
			f = (f << 6) | (ord(ustr[i]) & r)
	return f

class cn_char:
	often = [0x4E00, 0x9FFF]
	useless = [0x3400, 0x4DFF]
	history = [0x20000, 0x2A6DF]
	def contains(self, ucode):
		if (self.often[0] < ucode < self.often[1]) or \
		(self.useless[0] < ucode < self.useless[1]) or \
		(self.history[0] < ucode < self.history[1]):
			return True
		return False

class symbol_char:
	m = {}
	def __init__(self, fname):
		f = open(fname, "rb+")
		try:
			ss = f.read()
			i = 0
			l = len(ss)
			while True:
				_l = get_utf8_len(ss[i])
				if _l == 1:
					if ss[i] != "\n":
						self.m[get_utf8_code(ss[i], _l)] = True
					i += 1
				else:
					self.m[get_utf8_code(ss[i:i + _l], _l)] = True
					i += _l
				if i >= l:
					break
		finally:
			f.close()
	def contains(self, ucode):
		r = self.m.get(ucode) or False
		return r

class en_char:
	num = [ord('0'), ord('9')]
	bc = [ord('a'), ord('z')]
	sc = [ord('A'), ord('Z')]
		
	def contains(self, ucode):
		if (self.num[0] < ucode < self.num[1]) or \
		(self.bc[0] < ucode < self.bc[1]) or \
		(self.sc[0] < ucode < self.sc[1]):
			return True
		return False

class coarses:
	m = {}
	def __init__(self, fname):
		f = open(fname, "rb+")
		ss = f.read()

		ss = ss.split("\n")
		for k in ss:
			k = k.decode("utf-8", "ignore")
			self.m[k] = True

	def contains(self, word):
		return self.m.get(word)


def filte_symbols(string, cn_char_obj):
	rs = ""
	org_str_len = len(string)
	for i in range(0, org_str_len):
		ret = get_utf8_len(string[i])
		if ret == 1:
			pass
		elif ret == 3:
			char = string[i:i + ret]
			char_code = get_utf8_code(char, ret)
			if cn_char_obj.contains(char_code):
				rs += char
			i += (ret - 1)
		else:
			#ingore
			pass
	return rs

def chk_word(string, seg, coarses_dict, cn_char_obj, symbol_char_obj, en_char_obj):
	org_str_len = len(string)
	symbol_count = 0

	char_count = 0
	idx = 0

	while True:
		ret = get_utf8_len(string[idx])
		char_count += 1
		
		if ret == 1:
			char_code = get_utf8_code(string[idx], ret)
			if en_char_obj.contains(char_code):
				symbol_count += 1
			if symbol_char_obj.contains(char_code):
				symbol_count += 1
			idx += 1
		elif ret == 3:
			char = string[idx:idx + ret]
			char_code = get_utf8_code(char, ret)
			if symbol_char_obj.contains(char_code):
				symbol_count += 1
			idx += ret
		else:
			#ingore
			pass
		if idx >= org_str_len:
			break
	#fillte symbols if needed
	if (float(symbol_count) / float(char_count)) > 0.3:
		string = filte_symbols(string, cn_char_obj)
	
	string = seg.cut(string)
	for word in string:
		b = coarses_dict.contains(word)
		if b == True:
			return True
	
	return False

_localDir=os.path.dirname(__file__)
_curpath=os.path.normpath(os.path.join(os.getcwd(),_localDir))
curpath=_curpath

cn_char_obj = cn_char()
symbol_char_obj = symbol_char(os.path.join(curpath,"symbols.txt"))
en_char_obj = en_char()
coarses_dict = coarses(os.path.join(curpath,"./smallseg/coarses.txt"))
seg = smallseg.SEG("coarses.txt")


import commom
import json
redis_conn = commom.redis_conn

def get_one_packet():
	packet = redis_conn.brpop("coarse:filter:list")[1]
	return json.loads(packet)

def return_packet(extent_packet, has_coarse):
	return_packet = {
		"extent_packet": extent_packet,
		"has_coarse": has_coarse
	}

	json_packet = json.dumps(return_packet)
	redis_conn.lpush("filters:result:list", json_packet)

while True:
	try:
		packet = get_one_packet()
		message = packet["message"]
		message = commom.convert_uincode_to_string(message)
		
		extent_packet = packet["extent_packet"]

		has_coarse = chk_word(message, seg, coarses_dict, cn_char_obj, symbol_char_obj, en_char_obj)

		return_packet(extent_packet, has_coarse)
	except Exception, e:
		commom.report_error(commom.print_trace(e), "coarsefilter")


# f = open(os.path.join(curpath,"test.txt"), "rb+")
# lines = f.read()
# lines = lines.split("\n")

# for line in lines:
# 	print line,
# 	print chk_word(line, seg, coarses_dict, cn_char_obj, symbol_char_obj, en_char_obj)
	





