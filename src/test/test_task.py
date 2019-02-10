import sys
from os import getcwd
from os.path import join, abspath

current_folder = getcwd()
source_folder = abspath(join(current_folder, '..'))
sys.path.append(source_folder)

from Task import Task

insert_document_service_uri = 'http://runachay.evl.uic.edu:3020/api/insertFromPipe'
input_test_document_path = abspath(join(current_folder, '..', '..', 'output', 'p15350224'))
t = Task(insert_document_service_uri)

d = t.create_document(input_test_document_path)
#res = t.insert_document(d)
#print(str(res))
print d["figures"][0]["subfigures"][0]["uri"]