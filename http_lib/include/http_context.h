#ifndef __HTTP_CONTEXT__
#define __HTTP_CONTEXT__

#include <string>
#include <map>
#include <iostream>
#include <iostream>
#include "http_data.h"
// static const char *stop = "stop";
// static const char *dumped = "dumped";
// static const char *running = "running";
// static const char *service_stop	= "service_running";

namespace http_lib{

class http_context{
public:
	static http_data default_request_header;
	static const http_data none_http_data;

	static const int POST = 1;
	static const int GET = 0;
private:
	http_data 		_cookies;
	http_data 		_req_headers;
	std::string 	_sending_data;
	std::string 	_url;
	int				_timeout;
	int				_type;
public:
	http_context(const std::string &url, const http_data &cookies = none_http_data, const http_data &req_headers = none_http_data, int type = GET, const std::string &sending_data = "", int timeout = 20);

	void set_new_cookies(const http_data &cookies);
	void set_new_request_headers(const http_data &request_headers);
	void set_new_sending_data(const std::string &sending_data);
	void set_type(int type){
		_type = type;
	}

	void erase_cookie(const std::string &key){
		_cookies.erase(key);
	}

	void erase_reqest_header(const std::string &key){
		_req_headers.erase(key);
	}

	int type()const{
		return _type;
	}

	int timeout()const{
		return _timeout;
	}

	std::string sending_data() const{
		return _sending_data;
	}

	http_data cookies() const{
		return _cookies;
	}

	http_data request_headers() const{
		return _req_headers;
	}

	std::string url() const{
		return _url;
	}

	// std::shared_ptr<CURL> dumps();

	~http_context();
};

}

#endif //__HTTP_CONTEXT__