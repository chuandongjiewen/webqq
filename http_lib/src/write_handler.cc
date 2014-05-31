#include "write_handler.h"
#include "error_codes.h"
#include <exception>
#include <iostream>
using namespace std;
namespace http_lib{

size_t write_handler(void *buffer, size_t size, size_t nmemb, void *userp){
	USER_DATA *p = (USER_DATA *)userp;

	binary_buffer &bb = *(p->pbb);
	size_t len = size * nmemb;
	try{
		bb.put((char *)buffer, len);	
	}catch(exception &e){
		p->code = MALLOC_FAILED;
	}
	return len;
}

}