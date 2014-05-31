#include "http_context.h"
#include <curl/curl.h>

namespace http_lib{

class _init_{
public:
	_init_(){
		http_context::default_request_header["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8";
		http_context::default_request_header["Accept-Language"] = "zh-CN,zh;q=0.8";
		http_context::default_request_header["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36";
		http_context::default_request_header["Connection"] = "keep-alive";

		curl_global_init(CURL_GLOBAL_ALL);
	}

	~_init_(){
		curl_global_cleanup();
	}
};

//初始化
http_data http_context::default_request_header;
const http_data http_context::none_http_data;
static _init_ _ini;

}