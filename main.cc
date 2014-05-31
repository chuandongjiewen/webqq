#include <python2.7/Python.h>
#include <string>
#include <iostream>

#include <curl/curl.h>
#include <iostream>
#include "http_context.h"
#include "curl_dumper.h"
#include "binary_buffer.h"
#include "write_handler.h"
#include "http_result.h"
#include "http_service.h"
#include "base_error.h"
#include <string.h>
#include <regex>
#include <functional>
#include <string>
#include <utility>
#include <memory>
#include <unistd.h>

using namespace std;
using namespace http_lib;


http_data http_data_FromPyDict(PyObject *py_dict){
	http_data data;
	PyObject *key, *value;
	Py_ssize_t pos = 0;

	while (PyDict_Next(py_dict, &pos, &key, &value)) {
	    data[PyString_AsString(key)] = PyString_AsString(value);
	}

	return data;
}


void decrease_simple_PyDict(PyObject *py_dict){
	http_data data;
	PyObject *key, *value;
	Py_ssize_t pos = 0;
	while (PyDict_Next(py_dict, &pos, &key, &value)) {
	    Py_DECREF(key);
	    Py_DECREF(value);
	}

	//Py_DECREF(py_dict);
}

PyObject *dict_Ashttp_data(const http_data &data){
	http_data::const_iterator it = data.begin();
	http_data::const_iterator end = data.end();
	PyObject *dict = PyDict_New();
	if (!dict){
		return NULL;
	}
	for (; it != end; ++it){
		PyObject *key = PyString_FromString(it->first.c_str());
		if (!key){
			decrease_simple_PyDict(dict);
			return NULL;
		}
		PyObject *value = PyString_FromString(it->second.c_str());
		if (!value){
			decrease_simple_PyDict(dict);
			return NULL;
		}

		if (PyDict_SetItem(dict, key, value) != 0){
			decrease_simple_PyDict(dict);
			return NULL;
		}
	}

	return dict;
}

int get_cmd(PyObject *func){
	PyObject *p = PyObject_CallObject(func, NULL);
	int ret = PyLong_AsLong(p);
	Py_DECREF(p);
	return ret;
}

bool send_request_to_http_service(http_service *phs, PyObject *obj){

	PyObject *py_url = PyTuple_GetItem(obj, 0);
	PyObject *py_cookies = PyTuple_GetItem(obj, 1);
	PyObject *py_req_headers = PyTuple_GetItem(obj, 2);
	PyObject *py_req_type = PyTuple_GetItem(obj, 3);
	PyObject *py_sending_data = PyTuple_GetItem(obj, 4);
	PyObject *py_timeout = PyTuple_GetItem(obj, 6);

	http_context hc(PyString_AsString(py_url),
					http_data_FromPyDict(py_cookies),
					http_data_FromPyDict(py_req_headers),
					PyLong_AsLong(py_req_type),
					PyString_AsString(py_sending_data),
					PyLong_AsLong(py_timeout));


	PyObject *py_user_data = PyTuple_GetItem(obj, 5);
    char *user_data = PyString_AsString(py_user_data);

    shared_ptr<void> sud(malloc(strlen(user_data) + 1), free);
    if (sud == NULL){
    	fprintf(stderr, "Malloc failed\n");
    	return false;
    }

    strcpy((char *)sud.get(), user_data);
    phs->add_request(hc, sud);

    return true;

}

void delete_response_callback_paramter(PyObject *obj){
	if (obj != NULL){
		PyObject *py_cookies = PyTuple_GetItem(obj, 1);
		if (py_cookies != NULL){
			decrease_simple_PyDict(py_cookies);
		}
	}
}

PyObject *pack_response_callback_paramter(http_result &res, shared_ptr<void> user_data, int running_cnt){

	PyObject *pArgs = PyTuple_New(8);
	if (pArgs == NULL){
		if (PyErr_Occurred())
	        PyErr_Print();
	    fprintf(stderr, "Cannot create new tuple\n");
		return NULL;
	}

	PyObject *py_user_data = PyString_FromString((const char *)user_data.get());
	if (py_user_data == NULL){
		if (PyErr_Occurred()){
	    	PyErr_Print();
	    	delete_response_callback_paramter(pArgs);
	    	return NULL;
	    }
	    fprintf(stderr, "Cannot get user data from http_service\n");
	}
	PyTuple_SetItem(pArgs, 0, py_user_data);


	PyObject *py_cookies = dict_Ashttp_data(res.get_cookies());
	if (py_cookies == NULL){
		if (PyErr_Occurred()){
	    	PyErr_Print();
	    	delete_response_callback_paramter(pArgs);
	    	return NULL;
	    }
	    fprintf(stderr, "Cannot get cookies from http_service\n");
	}
	PyTuple_SetItem(pArgs, 1, py_cookies);


	PyObject *py_res_headers = PyString_FromString(res.get_response_headers().c_str());
	if (py_res_headers == NULL){
		if (PyErr_Occurred()){
	    	PyErr_Print();
	    	delete_response_callback_paramter(pArgs);
	    	return NULL;
	    }
	    fprintf(stderr, "Cannot get response headers from http_service\n");
	}
	PyTuple_SetItem(pArgs, 2, py_res_headers);

	size_t data_size = res.get_response_data()->size();
	//res.get_response_data()->put("\0", 1);
	PyObject *py_res_data = PyByteArray_FromStringAndSize((const char *)res.get_response_data()->data(), data_size);
	if (py_res_data == NULL){
		if (PyErr_Occurred()){
	    	PyErr_Print();
	    	delete_response_callback_paramter(pArgs);
	    	return NULL;
	    }
	    fprintf(stderr, "Cannot get response data from http_service\n");
	}
	PyTuple_SetItem(pArgs, 3, py_res_data);

	PyObject *py_data_size = PyLong_FromLong(data_size);
	if (py_data_size == NULL){
		if (PyErr_Occurred()){
	    	PyErr_Print();
	    	delete_response_callback_paramter(pArgs);
	    	return NULL;
	    }
	    fprintf(stderr, "Cannot get response data_size from http_service\n");
	}
	PyTuple_SetItem(pArgs, 4, py_data_size);


	PyObject *py_res_code = PyLong_FromLong(res.get_response_code());
	if (py_res_code == NULL){
		if (PyErr_Occurred()){
	    	PyErr_Print();
	    	delete_response_callback_paramter(pArgs);
	    	return NULL;
	    }
	    fprintf(stderr, "Cannot get response code from http_service\n");
	}
	PyTuple_SetItem(pArgs, 5, py_res_code);


	PyObject *py_curl_code = PyLong_FromLong(res.get_curl_code());
	if (py_curl_code == NULL){
		if (PyErr_Occurred()){
	    	PyErr_Print();
	    	delete_response_callback_paramter(pArgs);
	    	return NULL;
	    }
	    fprintf(stderr, "Cannot get curl code from http_service\n");
	}
	PyTuple_SetItem(pArgs, 6, py_curl_code);



	// //get running count
	PyObject *py_running_cnt = PyLong_FromLong(running_cnt);
	if (py_running_cnt == NULL){
		if (PyErr_Occurred()){
	    	PyErr_Print();
	    	delete_response_callback_paramter(pArgs);
	    	return NULL;
	    }
	    fprintf(stderr, "Cannot get curl code from http_service\n");
	}
	PyTuple_SetItem(pArgs, 7, py_running_cnt);


	return pArgs;
}


PyObject *call_callfun(PyObject *pFunc1, http_service *phs, bool &b, const char *qqnum, const char *passwd){

	PyObject *pArgs = PyTuple_New(3);
	if (pArgs == NULL){
		if (PyErr_Occurred())
	        PyErr_Print();
	    fprintf(stderr, "Cannot create new tuple\n");
	    b = false;
	    return NULL;
	}
	int running_cnt = phs->running_count();
	PyTuple_SetItem(pArgs, 0, PyLong_FromLong(running_cnt));
    PyTuple_SetItem(pArgs, 1, PyString_FromString(qqnum));
    PyTuple_SetItem(pArgs, 2, PyString_FromString(passwd));
	PyObject * pRet = PyObject_CallObject(pFunc1, pArgs);
	b = true;
	Py_DECREF(pArgs);
	return pRet;
}

#define PROCESS_CMD(pFuncCMD, action) ret = get_cmd(pFuncCMD); \
			   		if (ret == 1){ \
			   			bCMD_RENEW_SERVICE = true; \
			   			action; \
			   		} \
			   		if (ret == 2){ \
			   			bCMD_EXIT = true; \
			   			action; \
			   		}
int main(int argc, char *argv[]){
    
    if (argc < 3) {
        cout << "You must offer a qqnum and a passwd." << endl;
        return 0;
    }
    
    const char *qqnum = argv[1];
    const char *passwd = argv[2];
	
	//get the current work path
	char cwd[1024];
	strcpy(cwd, get_current_dir_name());

	PyObject *pName, *pModule, *pDict, *pFunc1, *pFunc2, *pFuncCMD, *pArgs;

	//set program path
	Py_SetProgramName(argv[0]);
	

	//init python interperter
	Py_Initialize();

	//append the current work path to the python sys.path
	PyObject *sys_path = PySys_GetObject("path");
	PyObject *pycwd = PyString_FromString(cwd);
	PyList_Append(sys_path, pycwd);
	Py_XDECREF(pycwd);


	//load the python protocol module
	pName = PyString_FromString("base_comunicate");
	pModule = PyImport_Import(pName);
	Py_DECREF(pName);

	if (pModule != NULL) {

		//get functions
		pFunc1 = PyObject_GetAttrString(pModule, "_call");
		pFunc2 = PyObject_GetAttrString(pModule, "_back");
		pFuncCMD = PyObject_GetAttrString(pModule, "_get_cmd");

		//check if the functions are all in good
		if (!(pFunc1 && PyCallable_Check(pFunc1))) {
	        if (PyErr_Occurred())
	            PyErr_Print();
	        fprintf(stderr, "Cannot find function \"_call\"\n");
	    }

	    if (!(pFunc2 && PyCallable_Check(pFunc2))) {
	        if (PyErr_Occurred())
	            PyErr_Print();
	        fprintf(stderr, "Cannot find function \"_back\"\n");
	    }

	    while (1){

	    	//init http_service object
			http_service *phs = new http_service();

			bool bCMD_EXIT = false;
	    	bool bCMD_RENEW_SERVICE = false;
	    	int ret;
	    	while (1){
				//call fun1 and get the dict return
				bool b;
				pDict = call_callfun(pFunc1, phs, b, qqnum, passwd);
				while (pDict != NULL){
					if (!PyTuple_Check(pDict)){
						break;
					}

					if (PyTuple_Size(pDict) != 7){
						break;
					}
					bool b;
					try{
						b = send_request_to_http_service(phs, pDict);
					}catch(std::exception &e){
						cout << e.what() << endl;
					}
					Py_DECREF(pDict);
					pDict = NULL;
			   		if (b == false){
			   			bCMD_EXIT = true;
			   			break;
			   		}

			   		PROCESS_CMD(pFuncCMD, break);

			   		pDict = call_callfun(pFunc1, phs, b, qqnum, passwd);
				}

				if (b == false){
					bCMD_EXIT = true;
				}

				Py_XDECREF(pDict);

				PROCESS_CMD(pFuncCMD, break);

				usleep(100000);

				vector<MULTI_RETURN> vec_mr(phs->poll());


			    vector<MULTI_RETURN>::iterator it = vec_mr.begin();
			    vector<MULTI_RETURN>::iterator end = vec_mr.end();
			    for (; it != end; ++it){
			    	PyObject *obj = pack_response_callback_paramter(it->hres, it->user_data, phs->running_count());
			    	PyObject *py_ret = PyObject_CallObject(pFunc2, obj);
			    	if (py_ret != NULL)
			    		Py_DECREF(py_ret);
			    	delete_response_callback_paramter(obj);
			    	
			    	// PyObject *py_ret = PyObject_CallObject(pFunc2, NULL);
			    	// Py_DECREF(py_ret);

			    	PROCESS_CMD(pFuncCMD, break);
			    }

			    if (!(pFunc1 && PyCallable_Check(pFunc1))) {
			        if (PyErr_Occurred())
			            PyErr_Print();
			        fprintf(stderr, "Cannot find function \"_call\"\n");
			        bCMD_EXIT = true;
			    }

			    if (!(pFunc2 && PyCallable_Check(pFunc2))) {
			        if (PyErr_Occurred())
			            PyErr_Print();
			        fprintf(stderr, "Cannot find function \"_back\"\n");
			        bCMD_EXIT = true;
			    }

			}

			delete phs;

			if (bCMD_EXIT){
 				break;
			}
		}

	    Py_XDECREF(pFunc2);
	    Py_XDECREF(pFunc1);
	    Py_XDECREF(pFuncCMD);
	    Py_DECREF(pModule);

	}else {
	    PyErr_Print();
	    fprintf(stderr, "Failed to load \"base_comunicate\"\n");
	    return 1;
	}
	Py_Finalize();
	return 0;

}