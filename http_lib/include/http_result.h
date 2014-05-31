#ifndef __HTTP_RESULT__
#define __HTTP_RESULT__

#include <string>
#include <map>
#include <memory>
#include <iostream>
#include "http_data.h"
#include <curl/curl.h>
#include "binary_buffer.h"
#include "curl_control.h"

namespace http_lib{

class http_result{
public:
	static http_data default_request_header;
	static const http_data none_http_data;

private:
	std::shared_ptr<binary_buffer>	_data;
	std::string						_resp_header;
	http_data 						_cookies;
	CURLcode 						_code;
	int 							_resp_code;
public:
	http_result(std::shared_ptr<binary_buffer> data = std::shared_ptr<binary_buffer>(NULL), 
		std::string resp_header = "", 
		std::shared_ptr<CURL_CONTROL> curl_ctrl = std::shared_ptr<CURL_CONTROL>(NULL), 
		CURLcode code = (CURLcode)0, 
		CURLMsg *msg = NULL);

	http_data get_cookies() const{
		return _cookies;
	}
	std::string get_response_headers() const{
		return _resp_header;
	}
	std::shared_ptr<binary_buffer> get_response_data() const{
		return _data;
	}
	int get_response_code() const{
		return _resp_code;
	}

	int get_curl_code() const{
		return _code;
	}

	~http_result();
};

}


#endif //__HTTP_CONTEXT__