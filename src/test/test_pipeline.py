import sys
from os import getcwd, listdir
from os.path import join, abspath
current_folder = getcwd()
source_folder = abspath(join(current_folder, '..'))
sys.path.append(source_folder)

from Pipeline import Pipeline

dependecies_folder = abspath(join(current_folder, '..', '..', 'dependencies', 'mac'))
chromedriver_path = join(dependecies_folder,'chromedriver')
xpdf_pdftohtml_path = join(dependecies_folder, 'xpdf-tools-mac-4.00', 'bin64', 'pdftohtml')
imagemagick_convert_path = join(dependecies_folder, 'ImageMagick-7.0.8', 'bin', 'convert')
figsplit_url = 'https://www.eecis.udel.edu/~compbio/FigSplit'
insert_document_service_uri = 'http://localhost:3020/api/insertFromPipe'
send_task_service_uri = 'http://localhost:3020/api/sendPipeTask'
logfilename = 'PipelineLog.txt'

ORGANIZATION = 'uic'
GROUPNAME = 'uic'

config = {
    'chromedriver_path': chromedriver_path,
    'xpdf_pdftohtml_path': xpdf_pdftohtml_path,
    'imagemagick_convert_path': imagemagick_convert_path,
    'figsplit_url': figsplit_url,
    'insert_document_service_uri': insert_document_service_uri,
    'send_task_service_uri': send_task_service_uri,
    'organization': ORGANIZATION,
    'groupname': GROUPNAME,
    'logfilename': logfilename
}

input_folder = abspath(join(current_folder, '..', '..', 'input', 'pipeline_input'))
output_folder = abspath(join(current_folder, '..', '..', 'output', 'pipeline_output'))
#input_document_path = join(input_folder, '15350224.pdf')

p = Pipeline(config)
input_documents = listdir(input_folder)
for input_doc in input_documents:
    input_document_path = join(input_folder, input_doc)
    result = p.process_file(input_document_path, output_folder)
