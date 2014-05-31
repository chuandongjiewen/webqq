#ifndef __HTTP_SERVICE_H__
#define __HTTP_SERVICE_H__
#include "http_context.h"
#include "curl_dumper.h"
#include "http_result.h"
#include "binary_buffer.h"
#include "write_handler.h"
#include <curl/curl.h>
#include <memory>
#include <map>
#include <vector>

namespace http_lib{

struct MULTI_RETURN
{
	MULTI_RETURN(http_result in_hres):hres(in_hres){}
	http_result hres;
	std::shared_ptr<void> user_data;
};

class http_service{
	struct _HTTP_SRV_CURL_CONTROL
	{
		_HTTP_SRV_CURL_CONTROL(std::shared_ptr<CURL_CONTROL> in_spcc = std::shared_ptr<CURL_CONTROL>(NULL), 
			std::shared_ptr<void> in_user_data = std::shared_ptr<void>(NULL)): 
		spcc(in_spcc), 
		sbb_data(std::shared_ptr<binary_buffer>(new binary_buffer)), 
		sbb_header(std::shared_ptr<binary_buffer>(new binary_buffer)),
		sud_data(std::shared_ptr<USER_DATA>(new USER_DATA)), 
		sud_header(std::shared_ptr<USER_DATA>(new USER_DATA)),
		user_data(in_user_data),
		sending_data(new std::string){
			sud_data->pbb = sbb_data.get();
			sud_header->pbb = sbb_header.get();

		}	

		std::shared_ptr<CURL_CONTROL> 	spcc;
		std::shared_ptr<binary_buffer> 	sbb_data;
		std::shared_ptr<binary_buffer>	sbb_header;

		std::shared_ptr<USER_DATA> 		sud_data;
		std::shared_ptr<USER_DATA> 		sud_header;
		std::shared_ptr<void> 			user_data;

		std::shared_ptr<std::string>	sending_data;
	};
	std::map<CURL *, _HTTP_SRV_CURL_CONTROL> _session_map;

	CURLM *_multi_handle;
	int _running_cnt;
public:
	http_service();
	void add_request(const http_context &hc, std::shared_ptr<void> user_data = std::shared_ptr<void>(NULL));
	std::vector<MULTI_RETURN> poll();

	int running_count(){
		_running_cnt = 0;
		curl_multi_perform(_multi_handle, &_running_cnt);
		return _running_cnt;
	}
	~http_service(){
		_session_map.clear();
		curl_multi_cleanup(_multi_handle);
	}
};

}
#endif //__HTTP_SERVICE_H__