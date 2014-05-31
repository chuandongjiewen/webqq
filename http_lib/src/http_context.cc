#include "http_context.h"
#include <exception>

using namespace std;

namespace http_lib{

http_context::http_context(const std::string &url, const http_data &cookies, const http_data &req_headers, int type, const string &sending_data, int timeout):
_url(url), _cookies(cookies), _req_headers(default_request_header), _type(type), _sending_data(sending_data), _timeout(timeout){
	_req_headers = combin_http_data(_req_headers, req_headers);

	if (req_headers.find("Host") == req_headers.end()){
		_req_headers["Host"] = url;
	}
}

void http_context::set_new_cookies(const http_data &cookies){
	_cookies = combin_http_data(_cookies, cookies);
}
void http_context::set_new_request_headers(const http_data &request_headers){
	_req_headers = combin_http_data(_req_headers, request_headers);
}
void http_context::set_new_sending_data(const string &sending_data){
	_sending_data = sending_data;
}


http_context::~http_context(){}

}
