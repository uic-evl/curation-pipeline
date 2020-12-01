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
print "saved document"
print saved_document

if saved_document:
    print "arg 0 " + saved_document[0]['_id']
    print "arg 1 " + saved_document[0]['name']
    task_result = t.send_task(saved_document[0]['_id'], saved_document[0]['name'], 'uic', 'uic')
    print task_result
    if task_result:
        print "Great!"
    else:
        print "Too bad"

#print(str(res))