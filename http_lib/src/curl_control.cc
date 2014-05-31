#include "curl_control.h"

#include <stdlib.h>
namespace http_lib{

void free_curl_control(CURL_CONTROL *p){
	if (p != NULL){
		if (p->request_headers != NULL)
			curl_slist_free_all(p->request_headers);
		if (p->easy_handle != NULL)
			curl_easy_cleanup(p->easy_handle);
		free(p);
	}	
}


}