import Image
import math
import redis

def get_median(l, i, j, ah, aw, mh, mw):
	tmp = []
	for ii in range(i, mh + i):
		for jj in range(j, mw + j):
			tmp.append(l[ii * aw + jj])

	tmp.sort()
	_l = len(tmp)
	idx = int(_l / 2)
	if _l % 2 == 0:
		return ((tmp[idx] + tmp[idx - 1]) / 2)
	else:
		return tmp[idx]

def media_filter(arr, ah, aw, mh, mw):
	b = mh % 2
	if b == 0:
		b = True
	else:
		b = False

	for i in range(0, ah):
		for j in range(0, aw):
			if (j + mw) < aw and (i + mh) < ah:
				ii = int(i + mh / 2)
				jj = int(j + mw / 2)
				if b:
					ii -= 1
				arr[ii * aw + jj] = get_median(arr, i, j, ah, aw, mh, mw)

def change_rgb(RGB):
	_RGB = [0, 0, 0]
	for i in range(0, 3):
		_RGB[i] = float(RGB[i]) / 255
	return _RGB

def hue(RGB):
	RGB = change_rgb(RGB)
	R = RGB[0]
	G = RGB[1]
	B = RGB[2]
	_max = max(RGB)
	_min = min(RGB)
	if _max == _min:
		return 0
	elif _max == R and G >= B:
		return 60 * (G - B) / (_max - _min)
	elif _max == R and G < B:
		return 60 * (G - B) / (_max - _min) + 360
	elif _max == G:
		return 60 * (B - R) / (_max - _min) + 120
	elif _max == B:
		return 60 * (R - G) / (_max - _min) + 240

def value(RGB):
	RGB = change_rgb(RGB)
	_max = max(RGB)
	return _max

def saturation(RGB):
	RGB = change_rgb(RGB)

	_max = max(RGB)
	_min = min(RGB)

	if _max == 0:
		return 0
	else:
		return (_max - _min) / _max


def image_filte(file_name):
	im = Image.open(file_name)


	aw, ah = im.size

	SCALE = max(int((aw + ah) / 320), 2)

	pic = list(im.getdata())
	l = len(pic)

	sx = 2
	sy = 2

	#media_filter(Rs, ah, aw, sx, sy)
	#media_filter(Gs, ah, aw, sx, sy)
	#media_filter(Bs, ah, aw, sx, sy)


	RGB = []
	CRs = []
	cnt = 0
	for idx in range(0, l):
		R = float(pic[idx][0])
		G = float(pic[idx][1])
		B = float(pic[idx][2])


		h = hue((R, G, B))
		s = saturation((R, G, B))
		v = value((R, G, B))

		if 0.5 <= v <= 38:
			#print h
			if 0 <= h <= 50:
				cnt += 1
		else:
			if 0 <= h <= 50 and 0.23 <= s <= 0.68:
				cnt += 1

	return float(cnt) / l



import commom
import json
redis_conn = commom.redis_conn

def get_one_packet():
	packet = redis_conn.brpop("image:filter:list")[1]
	return json.loads(packet)

def return_packet(extent_packet, skin_area):
	return_packet = {
		"extent_packet": extent_packet,
		"skin_area": skin_area
	}

	json_packet = json.dumps(return_packet)
	redis_conn.lpush("filters:result:list", json_packet)

while True:
	try:
		packet = get_one_packet()
		file_name = packet["file_name"]
		extent_packet = packet["extent_packet"]

		skin_area = image_filte(file_name)

		return_packet(extent_packet, skin_area)
	except Exception, e:
		commom.report_error(commom.print_trace(e), "imagefilter")


	#RGB.append((CR, CR, CR))
	# R = int(vall(R))
	# G = int(vall(G))
	# B = int(vall(B))

	# if R == 255 and G == 255 and B == 255:
	# 	R = 255
	# 	G = 0
	# 	B = 0

	#RGB.append((R, G ,B))


# for c in RGB:
# 	if c[0] != 0 and c[0] != 255:
# 		print c[0] 
	# CR = int(get_cr((R, G, B)))
 
	# RGB.append((CR, CR, CR))
# im2 = Image.new(im.mode, im.size)
# im2.putdata(RGB)
# im2.save("./rtest3.jpg")
###################