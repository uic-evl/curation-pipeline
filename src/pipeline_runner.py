import sys
import os
import json
from pprint import pprint
from os.path import exists, join
from os import mkdir, listdir
from Pipeline import Pipeline
from datetime import datetime

# sample execution:
# python pipeline_runner.py /Users/juan/Documents/Projects/Curation-Pipeline/src/config.json /Users/juan/Documents/Projects/Curation-Pipeline/input/pipeline_input /Users/juan/Documents/Projects/Curation-UI/dist/images 10

def main(argv):
    num_params = len(argv)
    if num_params < 4:
        print "Please provide the path to the configuration file, the input folder path, output folder " \
              "path and the maximum number of documents to process\n"
        return

    CONFIG_PATH = str(argv[0])
    if not exists(CONFIG_PATH):
        print "Cannot access the configuration file. Check the path and permissions.\n"
        return

    with open(CONFIG_PATH, 'r') as f:
        config_settings = json.load(f)
        pprint(config_settings)
    if not validate(config_settings):
        print "The configuration file is invalid. Check the README for instructions.\n"
        return

    INPUT_PATH = str(argv[1])
    if not exists(INPUT_PATH):
        print "Cannot access the input files. Check the path and permissions.\n"
        return

    # The pipeline will leave the images in the public dist folder from the web application
    WEBAPP_DIST_IMAGES_PATH = str(argv[2])
    if not exists(WEBAPP_DIST_IMAGES_PATH):
        try:
            mkdir(WEBAPP_DIST_IMAGES_PATH)
        except Exception as e:
            print "Could not create the output folder path"
            print e
            return

    MAX_NUMBER_DOCS_PROCESS = int(argv[3])

    number_docs_processed = 0
    pipeline = Pipeline(config_settings)
    input_documents = listdir(INPUT_PATH)

    log_file_path = join(WEBAPP_DIST_IMAGES_PATH, config_settings['logfilename'])
    with open(log_file_path, 'a+') as out:
        out.write('Batch execution:%s ---------------------\n' % (datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        out.write('%d documents found in input folder:\n' % len(input_documents))

    for input_doc in input_documents:
        if number_docs_processed < MAX_NUMBER_DOCS_PROCESS:
            input_document_path = join(INPUT_PATH, input_doc)
            if pipeline.process_file(input_document_path, WEBAPP_DIST_IMAGES_PATH):
                number_docs_processed += 1
        else:
            with open(log_file_path, 'a+') as out:
                out.write('Finished execution:%s ---------------------\n' % (datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                out.write('%d processed\n\n' % len(MAX_NUMBER_DOCS_PROCESS))
            print "Reached maximum number of documents to process. Stopping execution"
            return


def validate(config):
    if "chromedriver_path" not in config or not exists(config["chromedriver_path"]):
        print "Could not find the chromedriver.\n"
        return False
    if "xpdf_pdftohtml_path" not in config or not exists(config["xpdf_pdftohtml_path"]):
        print "Could not find the binary pdftohtml from xpdf.\n"
        return False
    if os.name == 'nt' and \
            ("imagemagick_convert_path" not in config or not exists(config["imagemagick_convert_path"])):
        print "Could not find the binary convert from imagemagick.\n"
        return False
    if "organization" not in config or config["organization"] == '':
        print "Could not find the organization.\n"
        return False
    if "groupname" not in config or config["groupname"] == '':
        print "Could not find the groupname.\n"
        return False
    if "figsplit_url" not in config:
        print "Could not find the url for the FigSplit service.\n"
        return False
    if "insert_document_service_uri" not in config:
        print "Could not find the url for the InsertDocument service.\n"
        return False
    if "send_task_service_uri" not in config:
        print "Could not find the url for the SendTask service.\n"
        return False
    return True


if __name__ == "__main__":
    main(sys.argv[1:])
