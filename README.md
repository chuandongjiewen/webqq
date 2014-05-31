===webqq===
	To the friends and the younger generation of Quanta.This is my graduation project which developed using Python and my favourite language C++.This webqq program can automatically recognize porn images,coarse words and advertisements.To achieve these goals it reads the chat messages form the QQ group and do some computing.Now I upload it to github offering the source for you to study and discuss.If you ask me why “You wrote the README.md in English”.Nothing I just want to encourage you to learn English.Because you want a high place, you want a promotion of your programming skills, you want English.So enough about the introduce.Let’s get to the point.
If you to setup this program.You will need these:
			1.Linux develop environment
			2.curl
			3.python2.7
			4.redis
			5.mysql
			6.redis-py
			7.MySQLdb
			8.mmseg 1.3.0 for python(https://pypi.python.org/pypi/mmseg/1.3.0)
You can get all of them through apt-get or easy_install or pip.It’s easy.Enough about how to set up the program.I’m going to make a simple guide for reading the source code.Basically my program have 4 layers(webqq layer, algorithms layer, middle layer and GUI layer).GUI layer isn’t written by me.So this repositories do not include any source code about GUI layer.
[webqq layer]
This is the core of this program.There’re 2 parts in this layer.Base communication part and protocol.Base communication is written in C++ using curl to offer a concurrent http request(Although I didn’t use any multiplexing APIs like epoll or select.Instead of this I used polling model for simplification purposes.Any body interested in this can try to rewrite it using epoll or select).There is a file names base_communicate.py put the C++ program and python program together.And the protocol.py contains some functions dealing with WebQQ Protocol.It’s hard to tell you all about the this layer.If you want to know more, read the source yourself.


[middle layer]
There’re 4 programs in the middle layer.
	receiver:
		Use to read the data comes from the webqq and check if the message of the 		sender is cached.If cached the packet will pass to dispatcher_webqq to 			decide how to deal with this packet,or the packet will pass to packetfixer 		to fix the missing cache.
	dispatcher_webqq:
		Dispatch the packet and write the data into mysql.
	packetfixer:
		Fix the missing cache and once this done,it pass the packet back to 			dispatcher_webqq.
	dispatcher_filter:
		Read the results from the filters(algorithms layer) and decide whether to 		send a warning message back to the QQ group.
	

[algorithms layer]
The coarse words filter simply use mmseg to extract words from the sentences and check if there is some coarse words.Any one who had the course “Natural Language” can understand this well.(coarse_filter.py)
The spam filter is written by WuYuanXiang.He used mmseg to extract words from sentences and Naive Bayes to recognise the advertisements from the message.(spamfilter.py)
The image filter simply use HSV colour model to compute and detect the human skin area to tell the porn images.(imagefilter.py)

	Ok,All of the introduce is over now.If you have any question,please contract me(QQ:176550981,email:yuhua6379@gmail.com)
	
