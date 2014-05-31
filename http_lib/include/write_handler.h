#ifndef __WRITE_HANDLER_H__
#define __WRITE_HANDLER_H__

#include "binary_buffer.h"
namespace http_lib{

size_t write_handler(void *buffer, size_t size, size_t nmemb, void *userp);
struct USER_DATA{
	binary_buffer *pbb;
	int	code;
};

}
#endif //__WRITE_HANDLER_H__