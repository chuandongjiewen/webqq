#encoding=utf-8
#import psyco
#psyco.full()
import os
import sys
import codecs
import chardet
import json
from smallseg import SEG
seg = SEG()
hashtable_good = {}
sum_files = 2450 #7439
g_allLen = 0

def cuttest(text, codec='utf-8'):
    wlist = seg.cut(text, codec)
    wlist.reverse()
    global g_allLen
    # tmp = " ".join(wlist)
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
        g_allLen += 1
    # print  tmp
    # print "================================"
    # return tmp.encode('utf8')
def handleRead(wlist):
    for i in wlist:
        if i == '\n':
            wlist.remove(i)
            continue
        if i[-1] == '\n':
            i = i[:-1]
    tmp = " ".join(wlist)
    return tmp
def calP(hashtable, filename):
    length = len(hashtable)
    global g_allLen
    for x in hashtable:
        hashtable[x]['rate'] = float(hashtable[x]['counts']) / g_allLen
    saveHashtable(hashtable, filename)
def getFilePath(filename):
    _localDir=os.path.dirname(__file__)
    _curpath=os.path.normpath(os.path.join(os.getcwd(),_localDir))
    curpath=_curpath
    realpath = os.path.join(curpath, filename)
    return realpath
    # self.set([x.rstrip() for x in file(os.path.join(curpath,"main.dic")) ])
    # self.specialwords= set([x.rstrip().decode('utf-8') for x in file(os.path.join(curpath,"suffix.dic"))])
def rebuildhashtable(text_list):
    hashtable = {}
    for x in text_list:
        x = x[:-1]#权宜之计，去除换行符用，因断网无力找……
        _temp = x.split('{')
        _tkey = _temp[0][:-1]
        _tkey = _tkey.decode('gb2312')
        del _temp[0]
        _tcontent = "{" + "".join(_temp)
        hashtable[_tkey] = eval(_tcontent)
    return hashtable
def readTextfromFile(filename):
    fileHandle = open(getFilePath(filename), 'r')
    _textlist = fileHandle.read()
    fileHandle.close()
    return _textlist
def saveHashtable(hashtable, filename):
    fileHandle = open(getFilePath(filename), 'w')
    # print hashtable
    # print fileHandle.read().decode('utf8')
    # for x in hashtable:
    #     # print(x + ":" + str(hashtable[x]))
    #     fileHandle.write((x + ":" + str(hashtable[x])).encode('gb2312'))
    #     fileHandle.write('\n')
    # fileHandle.close()
    hashtable = json.dumps(hashtable)
    fileHandle.write(hashtable)
    fileHandle.close()
if __name__=="__main__":
    # cuttest("干脆就把那部蒙人的闲法给废了拉倒！RT @laoshipukong : 27日，全国人大常委会第三次审议侵权责任法草案，删除了有关医疗损害责任“举证倒置”的规定。在医患纠纷中本已处于弱势地位的消费者由此将陷入万劫不复的境地。 ")
    cnt = 1
    while cnt < sum_files:
        fileName = 'sn/1 (' + str(cnt) + ').txt'
        _test = readTextfromFile(getFilePath(fileName))
        enc = chardet.detect(_test)
        if enc['encoding'] == 'GB2312':
            cuttest(_test, 'gb2312')
        else:
            cuttest(_test)
        print cnt
        cnt += 1
    calP(hashtable_good, getFilePath('new_hashtable_good1.txt'))
    # cuttest("本群仅此开放一小时！群号188027405验证码666（必填）赶快快点加这个群！群号236036838验证码666（必填）")
    # handleSeg(hashtable_bad, 'hashtable_bad.txt')
    # handleSeg(hashtable_good, 'hashtable_good.txt')
    # print hashtable_bad
    # fileHandle.write(hashtable_bad)
    # print rebuildhashtable(_textlist)
    # _rehash = rebuildhashtable(_textlist)
    # good_text = readTextfromFile('hashtable_good.txt')
    # hashtable_good = rebuildhashtable(good_text)
    # bad_text = readTextfromFile('hashtable_bad.txt')
    # hashtable_bad = rebuildhashtable(bad_text)