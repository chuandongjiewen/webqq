#ifndef __HTTP_EASY_SERVICE_H__
#define __HTTP_EASY_SERVICE_H__
#include "http_context.h"
#include "curl_dumper.h"
#include "http_result.h"
#include <memory>

namespace http_lib{
class http_easy_service{
	std::shared_ptr<CURL_CONTROL> 	_spcc;
public:
	http_easy_service();
	http_result poll(const http_context &hc);
};
}
#endif //__HTTP_EASY_SERVICE_H__