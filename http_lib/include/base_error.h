#ifndef __UTILITIES_H__
#define __UTILITIES_H__
#include <stdexcept>
#include <curl/curl.h>
#include <stdlib.h>
class base_error{
	std::runtime_error 	_err;
	int					_no;
	int					_code;
public:
	base_error(std::string strerr, int num, int code = CURLE_OK): _err(strerr), _no(num), _code(code){
	}

	std::string what() const{
		return _err.what();
	}

	int errnum() const{
		return _no;
	}

	int code()const{
		return _code;
	}

	~base_error(){}
};

#endif //__UTILITIES_H__