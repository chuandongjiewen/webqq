#include "curl_dumper.h"
#include <functional>
#include <utility>
#include "base_error.h"
#include "error_codes.h"
#include <assert.h>
#include "http_data.h"
using namespace std;

namespace http_lib{

void _get_list(const pair<string, string> &p, curl_slist **pp){
	string tmp = p.first + ": " + p.second;
	*pp = curl_slist_append(*pp, tmp.c_str());
}

void _get_cookie(const pair<string, string> &p, string *cookies){
	*cookies += (p.first + "=" + p.second + ";");
}

string concat_to_string(const http_data &data){
	string str_sending_data = "";
	http_data::const_iterator it = data.begin();
	http_data::const_iterator end = data.end();
	
	for (;it != end; ++it){
		str_sending_data += it->first + "=" + it->second;
		str_sending_data += "&";
	}

	str_sending_data = str_sending_data.substr(0, str_sending_data.length() - 1);

	return str_sending_data;
}


shared_ptr<CURL_CONTROL> curl_dumper::create_new_curl_control(){
	CURL_CONTROL *cc = (CURL_CONTROL *)malloc(sizeof(CURL_CONTROL));
	shared_ptr<CURL_CONTROL> spcc(cc, free_curl_control);

	if (cc == NULL){
		throw base_error("curl dump error:malloc failed", MALLOC_FAILED);
	}

	spcc->easy_handle = NULL;
	spcc->request_headers = NULL;

	CURL *tmp = curl_easy_init();
	if (tmp == NULL){
		throw base_error("curl dump error:curl_easy_init failed", CURL_EASY_INIT_FAILED);
	}

	spcc->easy_handle = tmp;

	return spcc;
}

void _dumps_request_headers(std::shared_ptr<CURL_CONTROL> spcc, const http_data &request_headers){
	if (request_headers.size() != 0){
		curl_slist *http_headers = NULL;
	
		for_each(request_headers.begin(), request_headers.end(), bind(_get_list, placeholders::_1, &http_headers));

		spcc->request_headers = http_headers;
		if (http_headers == NULL){
			throw base_error("curl dump error:init header failed", CURL_SLIST_ADDPEN_FAILED);
		}else{
			spcc->request_headers = http_headers;
			CURLcode err = curl_easy_setopt(spcc->easy_handle, CURLOPT_HTTPHEADER, http_headers);
			if (err != CURLE_OK){
				throw base_error("curl dump error:set CURLOPT_HTTPHEADER failed", CURL_EASY_SETOPT_FAILED, err);
			}
		}
	}
}

void _dumps_cookies(std::shared_ptr<CURL_CONTROL> spcc, const http_data &cookies){
	if (cookies.size() != 0){
		string str_cookies = "";
		try{
			for_each(cookies.begin(), cookies.end(), bind(_get_cookie, placeholders::_1, &str_cookies));
		}catch(exception &e){
			string err = "curl dump error:init cookie failed --- ";
			err + e.what();
			throw base_error(err, GET_COOKIE_FAILED);
		}
		assert(str_cookies != "");
		str_cookies = str_cookies.substr(0, str_cookies.size() - 1);

		CURLcode ret = curl_easy_setopt(spcc->easy_handle, CURLOPT_COOKIE, str_cookies.c_str());
		if (ret != CURLE_OK){
			throw base_error("curl dump error:init cookie failed", GET_COOKIE_FAILED, ret);
		}
	}
}

shared_ptr<CURL_CONTROL> curl_dumper::dump(std::shared_ptr<CURL_CONTROL> spcc, const http_data &request_headers, const http_data &cookies, const std::string &url, CURL_TRAN_FUNC fn, void *write_data, void *header_data){

	_dumps_request_headers(spcc, request_headers);

	_dumps_cookies(spcc, cookies);
	
	CURLcode ret = curl_easy_setopt(spcc->easy_handle, CURLOPT_URL, url.c_str());
	if (ret != CURLE_OK){
		throw base_error("curl dump error:set url failed", CURL_EASY_SETOPT_FAILED, ret);
	}
	ret = curl_easy_setopt(spcc->easy_handle, CURLOPT_WRITEHEADER, header_data);
	if (ret != CURLE_OK){
		throw base_error("curl dump error:set response header data failed", CURL_EASY_SETOPT_FAILED, ret);
	}
	ret = curl_easy_setopt(spcc->easy_handle, CURLOPT_WRITEDATA, write_data);
	if (ret != CURLE_OK){
		throw base_error("curl dump error:set write data failed", CURL_EASY_SETOPT_FAILED, ret);
	}
	ret = curl_easy_setopt(spcc->easy_handle, CURLOPT_WRITEFUNCTION, fn);
	if (ret != CURLE_OK){
		throw base_error("curl dump error:set write function failed", CURL_EASY_SETOPT_FAILED, ret);
	}
	ret = curl_easy_setopt(spcc->easy_handle, CURLOPT_COOKIEFILE, "");
	if (ret != CURLE_OK){
		throw base_error("curl dump error:activate cookie engine failed", CURL_EASY_SETOPT_FAILED, ret);
	}

	return spcc;

}

shared_ptr<CURL_CONTROL> curl_dumper::dump_in_get(std::shared_ptr<CURL_CONTROL> spcc, const http_data &request_headers, const http_data &cookies, const std::string &url, const string &sending_data, CURL_TRAN_FUNC fn, void *write_data, void *header_data){
	if (sending_data.length() >= 1024){
		throw base_error("curl dump error:get data too large", DATA_TOO_LARGE, CURLE_OK);
	}
	string _url = url;
	_url += "?";
	_url += sending_data;

	return curl_dumper::dump(spcc, request_headers, cookies, _url, fn, write_data, header_data);
}

shared_ptr<CURL_CONTROL> curl_dumper::dump_in_post(std::shared_ptr<CURL_CONTROL> spcc, const http_data &request_headers, const http_data &cookies, const std::string &url, const string &sending_data, CURL_TRAN_FUNC fn, void *write_data, void *header_data){
	CURLcode ret = CURLE_OK;

	ret = curl_easy_setopt(spcc->easy_handle, CURLOPT_POSTFIELDS, sending_data.c_str());
	if (ret != CURLE_OK){
		throw base_error("curl dump error:set post data error", CURL_EASY_SETOPT_FAILED, ret);
	}

	return curl_dumper::dump(spcc, request_headers, cookies, url, fn, write_data, header_data);
}

}