#ifndef __HTTP_DATA__
#define __HTTP_DATA__


#include <map>
#include <iostream>

namespace http_lib{

typedef std::map<std::string, std::string> http_data;
void print_http_data(const http_data &tmp);

http_data combin_http_data(const http_data &old_one, const http_data &new_one);

}
#endif //__HTTP_DATA__