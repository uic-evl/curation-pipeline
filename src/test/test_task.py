import sys
from os import getcwd
from os.path import join, abspath

current_folder = getcwd()
source_folder = abspath(join(current_folder, '..'))
sys.path.append(source_folder)

from Task import Task

insert_document_service_uri = 'http://localhost:3020/api/insertFromPipe'
send_task_service_uri = 'http://localhost:3020/api/sendPipeTask'
input_test_document_path = abspath(join(current_folder, '..', '..', 'output', 'p15350224'))
t = Task(insert_document_service_uri, send_task_service_uri)

d = t.create_document(input_test_document_path)
saved_document = t.insert_document(d)

if saved_document:
    task_result = t.send_task(saved_document['_id'], saved_document['name'], 'uic', 'uic')
    if task_result:
        print "Great!"
    else:
        print "Too bad"

#print(str(res))