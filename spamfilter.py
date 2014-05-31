# -*- coding: utf-8 -*-
import os
import sys
import json
import smallseg
#seg = smallseg.SEG("main.dic")
import mmseg
hashtable_bad = {}
hashtable_good = {}
cnt = 0
ad = 0
def seg_cut(text):
    results = mmseg.seg_txt(text)
    return_arr = []
    for item in results:
        return_arr.append(unicode(item, 'utf-8'))
    return return_arr
    # ret = seg.cut(text)
    # for item in ret:
    #     print item.encode("utf-8")
    # return ret
def cutsentence(text):
    wlist = seg_cut(text)
   # wlist = seg.cut(text)
    wlist.reverse()
    return checkSpam(wlist)
def cuttest(text):
    wlist = seg_cut(text)
    #wlist = seg.cut(text)
    wlist.reverse()
    tmp = " ".join(wlist)
    for i in wlist:
        if i == '':
            continue
        if i in hashtable_good:
            hashtable_good[i]['counts'] += 1
        else:
            hashtable_good[i] = {
                'counts':1,
                'rate':0
            }

def handleSeg(hashtable, filename):
    length = len(hashtable)
    for x in hashtable:
        hashtable[x]['rate'] = float(hashtable[x]['counts']) / length
    saveHashtable(hashtable, filename)

def getFilePath(filename):
    _localDir=os.path.dirname(__file__)
    _curpath=os.path.normpath(os.path.join(os.getcwd(),_localDir))
    curpath=_curpath
    realpath = os.path.join(curpath, filename)
    return realpath

def rebuildhashtable(text_list):
    hashtable = {}
    for x in text_list:
        x = x[:-1]#权宜之计，去除换行符用，因断网无力找……
        _temp = x.split('{')
        _tkey = _temp[0][:-1]
        _tkey = _tkey.decode('utf8')
        del _temp[0]
        _tcontent = "{" + "".join(_temp)
        hashtable[_tkey] = eval(_tcontent)
    return hashtable

def _rebuildhashtable(text_list):
    hashtable = json.loads(text_list[0])
    # for x in text_list:
    #     x = x[:-1]#权宜之计，去除换行符用，因断网无力找……
    #     _temp = x.split('{')
    #     _tkey = _temp[0][:-1]
    #     _tkey = _tkey.decode('utf8')
    #     del _temp[0]
    #     _tcontent = "{" + "".join(_temp)
    #     hashtable[_tkey] = eval(_tcontent)
    return hashtable


def readTextfromFile(filename):
    fileHandle = open(getFilePath(filename), 'r')
    _textlist = fileHandle.readlines()
    fileHandle.close()
    return _textlist

def saveHashtable(hashtable, filename):
    fileHandle = open(getFilePath(filename), 'w')
    for x in hashtable:
        fileHandle.write((x + ":" + str(hashtable[x])).encode('gb2312'))
        fileHandle.write('\n')
    fileHandle.close()

def checkSpam(sentence):
    s_d = {}.fromkeys(sentence).keys()
    p_spam = 0.1
    p_health = 0.9
    p_list = []
    p_list_good = []
    p_list_bad = []
    p_word_fin = 1
    p_word_sub = 1
    good_len = len(hashtable_good)
    bad_len = len(hashtable_bad)
    slen = len(s_d)
    global cnt
    global ad
    cnt += 1
    for words in s_d:
        if words not in hashtable_bad:
            p_word_spam = p_spam * slen / (slen + bad_len + good_len)
        else:
            p_word_spam = hashtable_bad[words]['rate']
        if words not in hashtable_good:
            p_word_health = p_health * slen / (slen + bad_len + good_len)
        else:
            p_word_health = hashtable_good[words]['rate']
        if p_word_spam == 0 and p_word_health == 0:
            continue
        else:
            p_word = p_word_spam * p_spam / (p_word_spam * p_spam + p_word_health * p_health)
        p_list.append(p_word)
        p_list_good.append(p_word_health)
        p_list_bad.append(p_word_spam)
    for r in p_list_bad:
        p_word_fin *= r
    for e in p_list_good:
        p_word_sub *= e
    p_word_fin *= p_spam
    p_word_sub *= p_health
    # print p_word_fin
    # print p_word_sub
    # print (p_word_fin > p_word_sub)
    return p_word_fin, p_word_sub
    # if p_word_fin > p_word_sub:
    #     # return p_word_fin, p_word_sub
    #     ad += 1
    #     return True
    # else:
    #     return False
    #p_final = p_word_fin / (p_word_fin + p_word_sub)

    #return p_final
    # print p_final
    # print (p_final > 0.9)

good_text = readTextfromFile('./check_spam/new_hashtable_good.txt')
hashtable_good = _rebuildhashtable(good_text)
bad_text = readTextfromFile('./check_spam/new_hashtable_bad.txt')
hashtable_bad = _rebuildhashtable(bad_text)

# print cutsentence("精准匹配，高点击高回报，付款及时 立即加入谷歌联盟，开始赚取美金!")

import commom
import json
redis_conn = commom.redis_conn

def get_one_packet():
    packet = redis_conn.brpop("spam:filter:list")[1]
    return json.loads(packet)

def return_packet(extent_packet, word_fin, word_sub):
    return_packet = {
        "extent_packet": extent_packet,
        "word_fin": word_fin,
        "word_sub": word_sub
    }

    json_packet = json.dumps(return_packet)
    redis_conn.lpush("filters:result:list", json_packet)

while True:
    try:
        packet = get_one_packet()
        message = packet["message"]
        message = commom.convert_uincode_to_string(message)
        extent_packet = packet["extent_packet"]

        p_word_fin, p_word_sub = cutsentence(message)
        
        return_packet(extent_packet, p_word_fin, p_word_sub)
    except Exception, e:
        commom.report_error(commom.print_trace(e), "spamfilter")

# cutsentence("本群仅此开放一小时！群号188027405验证码666（必填）赶快快点加这个群！群号236036838验证码666（必填）啊啊")
# cutsentence("想要兼职的朋友来找我 我也是业余在网上做兼职的 还不错的哦 大学生能赚到生活费的哦  20不嫌少，30不嫌多，积少成多方显理财大智慧。 想做+Q我的名字")
# cutsentence("由于本公司扩大经营，现急招聘淘宝兼职人员 招聘学生白领普通工人淘宝兼职 新开店铺刷信用只要你有能力不怕赚不到钱，多劳多得。天下没有白吃的午餐。只有自己的努力想做的联系我，如果觉得是骗人的，那你就该干嘛干嘛去。 1.有上网条件–兼 职/全职均可(在家中、办公室、网吧等地)。")
# cutsentence("这是一个伸手不见五指的黑夜。我叫孙悟空，我爱北京，我爱Python和C++。")
# cutsentence("我不喜欢日本和服。")
# cutsentence("雷猴回归人间。")
# cutsentence("工信处女干事每月经过下属科室都要亲口交代24口交换机等技术性器件的安装工作")
# cutsentence("我需要廉租房")
# cutsentence("永和服装饰品有限公司")
# cutsentence("我爱北京天安门")
# cutsentence("abc")
# cutsentence("隐马尔可夫")
# cutsentence("雷猴是个好网站")
# cutsentence("“Microsoft”一词由“MICROcomputer（微型计算机）”和“SOFTware（软件）”两部分组成")
# cutsentence("草泥马和欺实马是今年的流行词汇")
# cutsentence("伊藤洋华堂总府店")
# cutsentence("中国科学院计算技术研究所")
# cutsentence("罗密欧与朱丽叶")
# cutsentence("我购买了道具和服装")
# cutsentence("PS: 我觉得开源有一个好处，就是能够敦促自己不断改进，避免敞帚自珍")
# cutsentence("湖北省石首市")
# cutsentence("总经理完成了这件事情")
# cutsentence("电脑修好了")
# cutsentence("做好了这件事情就一了百了了")
# cutsentence("人们审美的观点是不同的")
# cutsentence("我们买了一个美的空调")
# cutsentence("线程初始化时我们要注意")
# cutsentence("一个分子是由好多原子组织成的")
# cutsentence("祝你马到功成")
# cutsentence("他掉进了无底洞里")
# cutsentence("中国的首都是北京")
# cutsentence("孙君意")
# cutsentence("外交部发言人马朝旭")
# cutsentence("领导人会议和第四届东亚峰会")
# cutsentence("在过去的这五年")
# cutsentence("还需要很长的路要走")
# cutsentence("60周年首都阅兵")
# cutsentence("你好人们审美的观点是不同的")
# cutsentence("买水果然后来世博园")
# cutsentence("买水果然后去世博园")
# cutsentence("但是后来我才知道你是对的")
# cutsentence("存在即合理")
# cutsentence("的的的的的在的的的的就以和和和")
# cutsentence("I love你，不以为耻，反以为rong")
# cutsentence("hello你好人们审美的观点是不同的")
# cutsentence("很好但主要是基于网页形式")
# cutsentence("hello你好人们审美的观点是不同的")
# cutsentence("为什么我不能拥有想要的生活")
# cutsentence("后来我才")
# cutsentence("此次来中国是为了")
# cutsentence("使用了它就可以解决一些问题")
# cutsentence(",使用了它就可以解决一些问题")
# cutsentence("其实使用了它就可以解决一些问题")
# cutsentence("好人使用了它就可以解决一些问题")
# cutsentence("是因为和国家")
# cutsentence("老年搜索还支持")
# cutsentence("想要做兼职吗？赶紧来加入这个群！")
# cutsentence("干脆就把那部蒙人的闲法给废了拉倒！RT @laoshipukong : 27日，全国人大常委会第三次审议侵权责任法草案，删除了有关医疗损害责任“举证倒置”的规定。在医患纠纷中本已处于弱势地位的消费者由此将陷入万劫不复的境地。 ")
# print ad
# print cnt