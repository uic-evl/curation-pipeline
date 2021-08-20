import sys
sys.path.append("..")

from Task import Task
from os import listdir
from os.path import join, isdir

insert_document_service_uri = ''
send_task_service_uri = ''

base_path = '/mnt'
folders = [join(base_path, x) for x in listdir(base_path) if isdir(join(base_path, x))]
group_name = "evaluators"
organization = "uic"
taxonomy = "curation"
token = ''

total = len(folders)
count = 0

for f in folders:
    if f == f'{base_path}/info':
        continue
    input_test_document_path = f

    try:
        t = Task(insert_document_service_uri, send_task_service_uri, token)
        d = t.create_document(input_test_document_path)

        saved_document = t.insert_document(d)
        print("saved document {0}".format(f))

        if saved_document:
            # print("arg 0 " + saved_document[0]['_id'])
            # print("arg 1 " + saved_document[0]['name'])
            print(saved_document)
            task_result = t.send_task(
                saved_document[0]['_id'], saved_document[0]['name'], organization, group_name, taxonomy)
            # print(task_result)
            if task_result:
                print("Great!")
                count += 1
            else:
                print("Too bad")
        else:
            print("error saving document")
    except Exception as e:
        print("Error with " + f)
        print(e)

print('processed {0}/{1}'.format(count, total))


# print(str(res))
