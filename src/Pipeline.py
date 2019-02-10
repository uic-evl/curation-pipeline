from ntpath import basename
from os.path import exists, join
from os import mkdir
from shutil import copy
from PDFigCapX import PDFigCapX
from FigSplitWrapper import FigSplitWrapper


class Pipeline:
    def __init__(self, _config):
        self.chromedriver_path = _config['chromedriver_path']
        self.xpdf_pdftohtml_path = _config['xpdf_pdftohtml_path']
        self.imagemagick_convert_path = _config['imagemagick_convert_path']
        self.figsplit_url = _config['figsplit_url']

    def process_file(self, _doc_path, _output_folder_container):
        if not exists(_doc_path):
            raise IOError
        if not exists(_output_folder_container):
            mkdir(_output_folder_container)

        filename = basename(_doc_path)
        doc_identifier = filename[:-4]

        document_folder_path = join(_output_folder_container, 'p' + doc_identifier)
        mkdir(document_folder_path)
        copy(_doc_path, join(document_folder_path, filename))

        fcx = PDFigCapX(self.chromedriver_path, self.xpdf_pdftohtml_path, self.imagemagick_convert_path)
        total_elems, total_figs, total_figs_success = fcx.extract(document_folder_path, document_folder_path)
        print "PDFigCapx (%d/%d)\n" % (total_figs_success, total_figs)

        fsw = FigSplitWrapper(self.figsplit_url)
        figcapx_output_path = join(document_folder_path, doc_identifier)
        total_splits, total_splits_success = fsw.split(figcapx_output_path)
        print "FigSplit (%d/%d)\n" % (total_splits_success, total_splits)


