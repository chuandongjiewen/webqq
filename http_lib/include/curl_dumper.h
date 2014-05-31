#ifndef __CURL_DUMPER__
#define __CURL_DUMPER__

#include <memory>
#include "http_data.h"
#include <algorithm>
#include <string>
#include <curl/curl.h>
#include "curl_control.h"
#include "binary_buffer.h"
namespace http_lib{

typedef size_t (*CURL_TRAN_FUNC)( void *ptr, size_t size, size_t nmemb, void *userdata);

class curl_dumper{
public:
	static std::shared_ptr<CURL_CONTROL> create_new_curl_control();
	static std::shared_ptr<CURL_CONTROL> dump(std::shared_ptr<CURL_CONTROL> spcc, const http_data &request_headers, const http_data &cookies, const std::string &url, CURL_TRAN_FUNC fn, void *write_data, void *header_data);
	static std::shared_ptr<CURL_CONTROL> dump_in_get(std::shared_ptr<CURL_CONTROL> spcc, const http_data &request_headers, const http_data &cookies, const std::string &url, const std::string &sending_data, CURL_TRAN_FUNC fn, void *write_data, void *header_data);
	static std::shared_ptr<CURL_CONTROL> dump_in_post(std::shared_ptr<CURL_CONTROL> spcc, const http_data &request_headers, const http_data &cookies, const std::string &url, const std::string &sending_data, CURL_TRAN_FUNC fn, void *write_data, void *header_data);
};

}

#endif //__CURL_DUMPER__