#include "http_easy_service.h"
#include "write_handler.h"
using namespace std;
namespace http_lib{

http_easy_service::http_easy_service(): _spcc(curl_dumper::create_new_curl_control()){

}


http_result http_easy_service::poll(const http_context &hc){

	shared_ptr<binary_buffer> spwd(new binary_buffer);
	binary_buffer bbh;


	USER_DATA write_data;
	write_data.pbb = spwd.get();

	USER_DATA header_data;
	header_data.pbb = &bbh;

	curl_easy_setopt(_spcc->easy_handle, CURLOPT_TIMEOUT, hc.timeout());
	if (hc.type() == http_context::GET){
		curl_dumper::dump_in_get(_spcc, hc.request_headers(), hc.cookies(), hc.url(), hc.sending_data(), write_handler, &write_data, &header_data);

	}else{
		curl_dumper::dump_in_post(_spcc, hc.request_headers(), hc.cookies(), hc.url(), hc.sending_data(), write_handler, &write_data, &header_data);
	}
	
	CURLcode code = curl_easy_perform(_spcc->easy_handle);

	
	return http_result(spwd, bbh.data(), _spcc, code);
}


}
