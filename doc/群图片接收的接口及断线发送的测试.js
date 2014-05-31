断线后发送测试，测试接口 "http://d.web2.qq.com/channel/poll2"
在登录之后等断线后再发，返回结果为 {"retcode":121,"t":"0"}
正常情况应为 {"retcode":102,"errmsg":""}



图片接收
     通过poll2得知是否有图片，字段

result[index_1][value][content][index_2][index_3]
index_1为result里面的位置，result可能有多个值
index_2为content里面的位置，一般应该为1
index_3为图片数据的位置，一般应该为1，0为字符串"cface"所在位置

{
    "retcode":0,
    "result":[
        {
            "poll_type":"group_message",
            "value":{
                "msg_id":30867,
                "from_uin":1075952639,
                "to_uin":2330453668,
                "msg_id2":507761,
                "msg_type":43,
                "reply_ip":176886375,
                "group_code":1915783259,
                "send_uin":708204531,
                "seq":6,
                "time":1393993455,
                "info_seq":376024301,
                "content":[
                    [
                        "font",
                        {
                            "size":18,
                            "color":"000000",
                            "style":[
                                1,
                                0,
                                0
                            ],
                            "name":"楷体"
                        }
                    ],
                    [
                        "cface",
                        {
                            "name":"{BEEC34D5-648F-9B3B-E356-EF4841744525}.jpg",
                            "file_id":2870896344,
                            "key":"uCyuyMfEBsBtvUt7",
                            "server":"183.60.18.38:8000"
                        }
                    ],
                    " "
                ]
            }
        }
    ]
}

访问'http://web2.qq.com/cgi-bin/get_group_pic'
     所需参数://可参考上面的json
          type//一般为0
          gid//与上面json的group_code相同
          uin//与上面的send_uin相同
          rip//与上面的server相同
          rport//可从上面的server中获取
          fid//与上面的file_id相同
          pic//与上面的name相同
          vfwebqq//在原python脚本里已有
          t//与上面的time相同

     所需cookie
          ts_refer=www.google.com.hk/; 
          pgv_pvi=1011700736; 
          RK=9nH2w4hl0q; 
          lv_irt_id=4a84d0030ac8c3bb518b9b5b88f49f7b; 
          o_cookie=340301018; 
          ts_last=web2.qq.com/; 
          ts_uid=1691876992; 
          pgv_pvid=2763058999; 
          pgv_info=ssid=s8320615942&pgvReferrer=; 
          verifysession=h026D_-pZV2oRiLA1NY7jTTb1b0B4HBhxvaV8TsJ18wLD7HzkGJTixiP_1193NBukgiuTbn4wUS3yoZwE42aAh9FA**; 
          ptui_loginuin=2330453668; 
          ptisp=ctc; 
          ptcz=edd0d2ced6bcaea1939315461541b5a941a07a48613ee2da04581e3d01316e81; 
          ptwebqq=f20d2367e4cad9df239daac10c607327c4c6d6594c91acb7d4dd1583ab99de19; 
          pt2gguin=o2330453668; 
          uin=o2330453668; 
          skey=@ZdKOGlQ7Q; 
          p_uin=o2330453668; 
          p_skey=xKUaF5zRFm2pmiO8CKYzpV3G5M0oKGqQM4Ow0T1zVBY_; 
          pt4_token=SM9EwWmc2SnJqdhGYjA3BQ__

//这是访问接口的http请求的headers
// GET /cgi-bin/get_group_pic?type=0&gid=1915783259&uin=708204531&rip=183.60.18.38&rport=8000&fid=2870896344&pic={BEEC34D5-648F-9B3B-E356-EF4841744525}.jpg&vfwebqq=d397a9881bd31501306c800a1910b24761adb0eb76785b9a35f63693336614acd0399450fb00980f&t=1393993455 HTTP/1.1
// Host: web2.qq.com
// Connection: keep-alive
// Accept: image/webp,*/*;q=0.8
// User-Agent: Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36
// Referer: http://web2.qq.com/webqq.html
// Accept-Encoding: gzip,deflate,sdch
// Accept-Language: zh-CN,zh;q=0.8,en;q=0.6
// Cookie: ts_refer=www.google.com.hk/; pgv_pvi=1011700736; RK=9nH2w4hl0q; lv_irt_id=4a84d0030ac8c3bb518b9b5b88f49f7b; o_cookie=340301018; ts_last=web2.qq.com/; ts_uid=1691876992; pgv_pvid=2763058999; pgv_info=ssid=s8320615942&pgvReferrer=; verifysession=h026D_-pZV2oRiLA1NY7jTTb1b0B4HBhxvaV8TsJ18wLD7HzkGJTixiP_1193NBukgiuTbn4wUS3yoZwE42aAh9FA**; ptui_loginuin=2330453668; ptisp=ctc; ptcz=edd0d2ced6bcaea1939315461541b5a941a07a48613ee2da04581e3d01316e81; ptwebqq=f20d2367e4cad9df239daac10c607327c4c6d6594c91acb7d4dd1583ab99de19; pt2gguin=o2330453668; uin=o2330453668; skey=@ZdKOGlQ7Q; p_uin=o2330453668; p_skey=xKUaF5zRFm2pmiO8CKYzpV3G5M0oKGqQM4Ow0T1zVBY_; pt4_token=SM9EwWmc2SnJqdhGYjA3BQ__

// HTTP/1.1 302 OK
// Connection: close
// Date: Wed, 05 Mar 2014 04:24:16 GMT
// Content-Length: 1
// Location: http://gchat.qpic.cn/gchatpic/2641024301/2641024301-2870896344-BEEC34D5648F9B3BE356EF4841744525/0
// Content-Type: text/html


     返回结果
          // HTTP/1.1 302 OK
          // Connection: close
          // Date: Wed, 05 Mar 2014 04:24:16 GMT
          // Content-Length: 1
          // Location: http://gchat.qpic.cn/gchatpic/2641024301/2641024301-2870896344-BEEC34D5648F9B3BE356EF4841744525/0
          // Content-Type: text/html

          其中Location的值即为图片地址
