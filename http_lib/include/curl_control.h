#ifndef __CURL_CONTROL__
#define __CURL_CONTROL__
#include <curl/curl.h>

namespace http_lib{

struct CURL_CONTROL{
	CURL *easy_handle;
	curl_slist *request_headers;
};

void free_curl_control(CURL_CONTROL *p);

}

#endif //__CURL_CONTROL__
