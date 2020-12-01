from ntpath import basename
from os.path import exists, join
from os import mkdir
from shutil import copy, rmtree
from PDFigCapX import PDFigCapX
from FigSplitWrapper import FigSplitWrapper
from Task import Task
from datetime import datetime


class Pipeline:
    def __init__(self, _config):
        self.chromedriver_path = _config['chromedriver_path']
        self.xpdf_pdftohtml_path = _config['xpdf_pdftohtml_path']
        self.imagemagick_convert_path = _config['imagemagick_convert_path']
        self.figsplit_url = _config['figsplit_url']
        self.insert_document_service_uri = _config['insert_document_service_uri']
        self.send_task_service_uri = _config['send_task_service_uri']
        self.organization = _config['organization']
        self.group_name = _config['groupname']
        self.log_filename = _config['logfilename']

    def process_file(self, _doc_path, _output_folder_container):
        if not exists(_doc_path):
            raise IOError
        if not exists(_output_folder_container):
            mkdir(_output_folder_container)

        filename = basename(_doc_path)
        doc_identifier = filename[:-4]

        # Create the output folder for the extracted content and place the PDF inside
        document_folder_path = join(_output_folder_container, 'p' + doc_identifier)
        if exists(document_folder_path):
            error = "output document folder path exists, skipping document %s" % filename
            self.log_error(_output_folder_container, error)
            return None
        mkdir(document_folder_path)
        copy(_doc_path, join(document_folder_path, filename))

        # Extract figures and captions
        fcx = PDFigCapX(self.chromedriver_path, self.xpdf_pdftohtml_path, self.imagemagick_convert_path)
        total_elems, total_figs, total_figs_success = fcx.extract(document_folder_path, document_folder_path)
        print("PDFigCapx (%d/%d)\n" % (total_figs_success, total_figs))
        if total_figs_success != total_figs:
            error = "PDFigCapX could not process all the content for %s" % filename
            self.log_error(_output_folder_container, error)
            self.remove_folder(document_folder_path, _output_folder_container)
            return None

        # Split the figures in the document
        fsw = FigSplitWrapper(self.figsplit_url)
        figcapx_output_path = join(document_folder_path, doc_identifier)
        total_splits, total_splits_success = fsw.split(figcapx_output_path)
        print("FigSplit (%d/%d)\n" % (total_splits_success, total_splits))
        if total_splits_success != total_splits:
            error = "FigSplit could not process all the figures for %s" % filename
            self.log_error(_output_folder_container, error)
            self.remove_folder(document_folder_path, _output_folder_container)
            return None

        task_service = Task(self.insert_document_service_uri, self.send_task_service_uri)
        document = task_service.create_document(document_folder_path)
        saved_document, saving_error = task_service.insert_document(document)
        if saved_document:
            task = task_service.send_task(saved_document['_id'], saved_document['name'],
                                                  self.organization, self.group_name)
            if task:
                return task
            else:
                error =  "Error creating task"
                self.log_error(_output_folder_container, error)
                self.remove_folder(document_folder_path, _output_folder_container)
        else:
            error = "Error inserting document in the database \n" + saving_error
            self.log_error(_output_folder_container, error)
            self.remove_folder(document_folder_path, _output_folder_container)
        return None

    def remove_folder(self, folder_path, _output_folder_container):
        try:
            rmtree(folder_path)
        except Exception as e:
            error = "Error deleting folder"
            self.log_error(_output_folder_container, error)
            print(e)

    def log_error(self, output_folder, message):
        log_file_path = join(output_folder, self.log_filename)
        with open(log_file_path, 'a+') as out:
            out.write('%s:%s\n' % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message))
