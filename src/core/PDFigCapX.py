import json
import subprocess
import time
from . import renderer
import os
import execnet

from os import mkdir, listdir
from os.path import join, isdir

PDF_OUTPUT_FOLDER = 'xpdf_'
LOG_FILE = 'PDFigCapXlog.txt'
MAX_WRONG_COUNT = 5


class PDFigCapX():
    """ Extract the figures and captions from PDF documents.
    PDFigCapx extracts the figures and captions from all the documents in
    an input path an places them in a given output path. For each PDF, it
    creates a folder with the document name and a folder with the document
    name and the prefix _xpdf. The _xpdf folder contains the outputs from
    the extraction tools.
    In a Linux environment, this class depends on the installation of
    ghostscript and gsfonts (Type 1 and X11). Also, the system local should
    support UTF-8. The current implementation is heavily dependent on a
    Python 2.7 installation to execute figures_captions_list, which is here
    wrapped in execnet. For the docker installation, we are hardcoding the
    location of the compiled files pdf_info.pyc and xpdf_process.pyc which
    are maintained by Pengyuan Li.
    Attributes:
        _chrome_drive_path: path to chromedriver. e.g. /usr/bin/chromedriver
        _xpdf_pdftohtml_path: path to bin64/pdftohtml in xpdf tools.
        _imagemagick_convert_path: path to convert.exe in imagemagick. Only
          relevant for windows systems.
    """

    def __init__(self,
                _dpi=300,
                _chrome_drive_path='/usr/bin/chromedriver',
                _xpdf_pdftohtml_path='/usr/local/bin/pdftohtml',
                _imagemagick_convert_path=None):
        self.chrome_driver_path = _chrome_drive_path
        self.xpdf_pdftohtml_path = _xpdf_pdftohtml_path
        self.imagemagick_convert_path = _imagemagick_convert_path        
        self.dpi = _dpi
        self.log_file = None

    def extract(self, _input_path, _output_path):
        xpdf_output_path_prefix = join(_output_path, PDF_OUTPUT_FOLDER)  # /.../xpdf_
        log_file_path = join(_output_path, LOG_FILE)
        total_extracted = 0
        total_pdfs = 0
        pdf_err_list = []

        try :            
            self.log_file = open(log_file_path, 'w')
            pdfs = [x for x in listdir(_input_path) if x[0] != '_' and '.pdf' in x.lower() and os.path.isfile(join(_input_path, x))]

            for pdf in pdfs:
                total_pdfs += 1
                pdf_path = join(_input_path, pdf)

                pil_images = renderer.render_pdf(pdf_path, self.imagemagick_convert_path, dpi=self.dpi)                    

                if self.__convert_pdf_to_html(xpdf_output_path_prefix, pdf, pdf_path):
                    if self.__process_figures(pil_images, _input_path, pdf, xpdf_output_path_prefix, _output_path):
                        total_extracted += 1
                    else:
                        pdf_err_list.append(pdf)
            return pdf_err_list, total_pdfs, total_extracted
        finally:
            self.log_file.close()        

    def __convert_pdf_to_html(self, _xpdf_output_path, _pdf, _pdf_path):
        try:            
            xpdf_pdf_path = _xpdf_output_path + _pdf[:-4]  # xpdf_{pdf_name_without_extension}
            if not isdir(xpdf_pdf_path):
                # execute xpdf if folder does not exist
                std_out = subprocess.check_output([self.xpdf_pdftohtml_path, _pdf_path, xpdf_pdf_path])
            return True
        except Exception as e:
            self.log_file.write("ERROR: %s\t%s\n%s\n" % (_pdf, "xpdf_to_html", e))
            return False

    def py2_wrapper(self, input_path, pdf, xpdf_output_path, chromedriver):
        # invoke python 2.7 (in Docker as python)
        try:
            group = execnet.Group()
            gw = group.makegateway("popen//python=python")
            channel = gw.remote_exec("""
                import sys
                sys.path.append('/home/curation-pipeline/compiled')
                from xpdf_process import figures_captions_list
                channel.send(figures_captions_list(*channel.receive()))
                """)
            channel.send([input_path, pdf, xpdf_output_path, chromedriver])
            result = channel.receive()            
            return result        
        finally:
            group.terminate(timeout=1.0)


    def __extract_figures(self, _input_path, _pdf, _xpdf_output_path):
        flag = 0
        wrong_count = 0
        figures = []
        info = None

        while flag == 0 and wrong_count < MAX_WRONG_COUNT:
            try:
                # process content using the ChromeDriver
                figures, info = self.py2_wrapper(_input_path, _pdf, _xpdf_output_path, self.chrome_driver_path)
                flag = 1
            except Exception as e:
                flag = 0
                wrong_count += 1
                time.sleep(5)
                print("error _extract_figures")
                self.log_file.write("ERROR: %s\t%s\n%s" % (_pdf, "_extract_figures (%d/%d)".format(wrong_count, MAX_WRONG_COUNT), e))

            return figures, info, flag

    def __process_figures(self, _images, _input_path, _pdf, _xpdf_output_path, _output_path):
        data = {}
        data[_pdf] = {
            'figures': [],
            'pages_annotated': []
        }

        figures, info, flag = self.__extract_figures(
            _input_path, _pdf, _xpdf_output_path)
        if flag == 0:  # there was an error in the extraction
            return False

        data[_pdf]['fig_no'] = info['fig_no_est']
        # the output images and captions are stored in a folder with the pdf name
        output_file_path = join(_output_path, _pdf[:-4])
        if not isdir(output_file_path):
            mkdir(output_file_path)

        for figure in figures:
            page_no = int(figure[:-4][4:])
            page_fig = _images[page_no - 1]
            rendered_size = page_fig.size

            bboxes = figures[figure]
            order_no = 0
            for bbox in bboxes:
                order_no = order_no + 1
                png_ratio = float(rendered_size[1]) / info['page_height']

                if len(bbox[1]) > 0:
                    data[_pdf]['figures'].append(
                        {
                            'page': page_no,
                            'region_bb': bbox[0],
                            'figure_type': 'Figure',
                            'page_width': info['page_width'],
                            'page_height': info['page_height'],
                            'caption_bb': bbox[1][0],
                            'caption_text': bbox[1][1]
                        })
                    caption_output_filepath = join(
                        output_file_path, '%d_%d.txt' % (page_no, order_no))
                    with open(caption_output_filepath, 'w') as capoutput:
                        # print len(bbox[1][1])
                        # print bbox[1][1]
                        # capoutput.write(str(bbox[1][1]))
                        content = ''.join(bbox[1][1])
                        capoutput.write(content)
                else:
                    data[_pdf]['figures'].append(
                        {
                            'page': page_no,
                            'region_bb': bbox[0],
                            'figure_type': 'Figure',
                            'page_width': info['page_width'],
                            'page_height': info['page_height'],
                            'caption_bb': [],
                            'caption_text': []
                        })
                fig_extracted = page_fig.crop([int(bbox[0][0] * png_ratio), int(bbox[0][1] * png_ratio),
                                               int((bbox[0][0] + bbox[0][2]) * png_ratio), int((bbox[0][1] + bbox[0][3]) * png_ratio)])
                fig_filepath = join(
                    output_file_path, '%d_%d.jpg' % (page_no, order_no))
                fig_extracted.save(fig_filepath)

        json_file = join(output_file_path, '%s.json' % _pdf[:-4])
        with open(json_file, 'w') as outfile:
            json.dump(data[_pdf], outfile, ensure_ascii=False)
        return True
