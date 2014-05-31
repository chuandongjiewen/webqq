#include "http_service.h"
#include "base_error.h"
#include "error_codes.h"
#include "http_result.h"
#include <assert.h>
#include <iostream>
namespace http_lib{

	using namespace std;

http_service::http_service():_multi_handle(curl_multi_init()){
	if (_multi_handle == NULL){
		throw base_error("http service:curl_multi_init failed", CURL_MULTI_INIT_FAILED);
	}
}

void http_service::add_request(const http_context &hc, shared_ptr<void> user_data){
	_HTTP_SRV_CURL_CONTROL hscc(curl_dumper::create_new_curl_control(), user_data);
	*hscc.sending_data = hc.sending_data();

	CURL *easy_handle = hscc.spcc->easy_handle;

	curl_easy_setopt(easy_handle, CURLOPT_TIMEOUT, hc.timeout());
	if (hc.type() == http_context::GET){
		curl_dumper::dump_in_get(hscc.spcc, hc.request_headers(), hc.cookies(), hc.url(), *hscc.sending_data, write_handler, hscc.sud_data.get(), hscc.sud_header.get());

	}else{
		curl_dumper::dump_in_post(hscc.spcc, hc.request_headers(), hc.cookies(), hc.url(), *hscc.sending_data, write_handler, hscc.sud_data.get(), hscc.sud_header.get());
	}

	CURLMcode ret = curl_multi_add_handle(_multi_handle, easy_handle);
	if (ret != CURLM_OK){
		throw base_error("http service error:curl_multi_add_handle error", CURL_MULTI_ADD_HANDLE_FAILED, ret);
	}

	std::pair<CURL *, _HTTP_SRV_CURL_CONTROL> p(easy_handle, hscc);
	_session_map.insert(p);
}


std::vector<MULTI_RETURN> http_service::poll(){
	_running_cnt = 0;
	curl_multi_perform(_multi_handle, &_running_cnt);
	int msg_cnt = 0;
	CURLMsg *msg = curl_multi_info_read(_multi_handle, &msg_cnt);
	
	std::vector<MULTI_RETURN> ret;
	while(msg != NULL){
		assert(msg->msg == CURLMSG_DONE);
		CURL *easy_handle = msg->easy_handle;
		_HTTP_SRV_CURL_CONTROL hscc = _session_map[easy_handle];

		hscc.sbb_header->put("\0", 1);
		http_result hres(hscc.sbb_data, hscc.sbb_header->data(), hscc.spcc, msg->data.result);
		MULTI_RETURN mr(hres);
		mr.user_data = hscc.user_data;
		ret.push_back(mr);

		curl_multi_remove_handle(_multi_handle, easy_handle);
		_session_map.erase(easy_handle);

		msg = curl_multi_info_read(_multi_handle, &msg_cnt);
	}

	return ret;
}

}