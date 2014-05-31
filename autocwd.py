import os

old_wd = os.getcwd()
def get_current_path():
	return os.path.dirname(__file__)

def get_old_wd():
	return old_wd

os.chdir(get_current_path())
