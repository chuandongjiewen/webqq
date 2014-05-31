#include "http_data.h"
namespace http_lib{

void print_http_data(const http_data &tmp){
	http_data::const_iterator it = tmp.begin();
	http_data::const_iterator end = tmp.end();

	for (; it != end; ++it){
		std::cout << it->first << ": " << it->second << std::endl;
	}
}
http_data combin_http_data(const http_data &old_one, const http_data &new_one){
	http_data ret = old_one;
	http_data::const_iterator it = new_one.begin();
	http_data::const_iterator end = new_one.end();

	for (; it != end; ++it){
		ret[it->first] = it->second;
	}

	return ret;
}

}
