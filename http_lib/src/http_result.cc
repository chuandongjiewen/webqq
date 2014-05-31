#include "http_result.h"
#include "http_context.h"
#include "base_error.h"
#include "error_codes.h"
using namespace std;


namespace http_lib{

static http_data _get_cookies(CURL *easy_handle){
	struct curl_slist *cookies;
	struct curl_slist *nc;
	
	CURLcode ret = curl_easy_getinfo(easy_handle, CURLINFO_COOKIELIST, &cookies);
	if (ret != CURLE_OK){
		return http_context::none_http_data;
	}

	http_data ret_data;

	
	nc = cookies;
	while (nc) {
		char *data = nc->data;
		char *pch = strtok(data, "\t");
		int i = 0;
		string k;
		string v;
		
		while (pch != NULL)
		{	
			++i;
			if (i == 6)
				k = pch;
				
			if (i == 7)
				v = pch;
			
			pch = strtok(NULL, "\t");
		}

		ret_data[k] = v;
		nc = nc->next;
		
	}

	return ret_data;
}


http_result::http_result(std::shared_ptr<binary_buffer> data, string resp_header, std::shared_ptr<CURL_CONTROL> curl_ctrl, CURLcode code, CURLMsg *msg):
_data(data), _resp_header(resp_header), _code(code){
	//if (msg == NULL)
	
	int http_code = 0;
	CURLcode ret = curl_easy_getinfo (curl_ctrl->easy_handle, CURLINFO_RESPONSE_CODE, &http_code);
	if (ret != CURLE_OK){
		throw base_error("http result:get response status code failed", CURL_EASY_SETOPT_FAILED, ret);
	}

	if (msg != NULL){
		_code = msg->data.result;
	}

	_resp_code = http_code;
	_cookies = _get_cookies(curl_ctrl->easy_handle);
}

http_result::~http_result(){
	
}

// http_data http_result::get_new_cookies() const{

// }

// http_data http_result::get_response_headers() const{

// }
// const char *http_result::get_response_data() const{

// }
// int http_result::get_response_code() const{

// }

// int http_result::get_curl_code() const{

// }

// http_result::~http_result(){

// }


}
