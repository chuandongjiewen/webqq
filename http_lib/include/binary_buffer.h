#ifndef __BINARY_BUFFER_H__
#define __BINARY_BUFFER_H__
#include <stdexcept>
#include <exception>
#include <stdlib.h>
#include <memory.h>
class binary_buffer{
	char *_data;
	size_t _size;
	size_t _left;
	size_t _idx;
public:
	binary_buffer(size_t init_size = 1024): _idx(0){
		_data = (char *)malloc(init_size);

		if (_data == NULL){
			throw std::runtime_error("no memory");
		}
		_size = init_size;
		_left = init_size;
	}

	size_t size() const{
		return _idx;
	}
	void put(const char *data, size_t len){
		while (_left < len){
			size_t new_size = _size * 2;
			char *new_data = (char *)realloc(_data, new_size);
			if (new_data == NULL){
				throw std::runtime_error("no memory");
			}

			_data = new_data;
			_left += _size;
			_size = new_size;
		}

		memcpy(_data + _idx, data, len);
		_idx += len;
		_left -= len;
	}

	const char *data() const{
		return _data;
	}


	~binary_buffer(){
		free(_data);
	}

};

#endif //__BINARY_BUFFER_H__