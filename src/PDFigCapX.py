import json
import subprocess
import time
import renderer
import os
import execnet
import pandas as pd


from os import mkdir, listdir
from os.path import join, isdir

PDF_OUTPUT_FOLDER = 'xpdf_'
LOG_FILE = 'PDFigCapXlog.log'
CONSOLE_OUTPUT = 'extract.log'
MAX_WRONG_COUNT = 5
ERROR_FILE = "extract_error.log"
TRACKER_FILE = "extract_track.csv"

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

    def __init__(self, _chrome_drive_path='/usr/bin/chromedriver',
                 _xpdf_pdftohtml_path='/usr/local/bin/pdftohtml',
                 _imagemagick_convert_path=None):
        self.chrome_driver_path = _chrome_drive_path
        self.xpdf_pdftohtml_path = _xpdf_pdftohtml_path
        self.imagemagick_convert_path = _imagemagick_convert_path
        self.log_file = None
        self.dpi = os.getenv('DPI') or 300

    def extract(self, _input_path, _output_path, _log_path, _filterProccessed):
        xpdf_output_path_prefix = join(_output_path, PDF_OUTPUT_FOLDER)  # xpdf_path
        log_file_path = join(_log_path, LOG_FILE)
        
        self.log_file = open(log_file_path, 'a')
        
        self.error_file = join(_log_path, ERROR_FILE)
        self.track_file = join(_log_path, TRACKER_FILE)
        self.console_output = join(_log_path, CONSOLE_OUTPUT)
        self.directory = _input_path.split('/')[-1]
        self.total_time = 0

        # process each pdf file in the input folder
        files = listdir(_input_path)
        success = 0
        total_pdf = 0
        errorMessage = ''

        if (_filterProccessed):
            files = self.filterProcessed(files)

        for pdf in files:
            if (pdf.endswith('.pdf') or pdf.endswith('.PDF')) and not pdf.startswith('._'):

                name = pdf[:-4]
                directory = xpdf_output_path_prefix + name
                if not os.path.isdir(directory):

                    total_pdf += 1
                    pdf_path = join(_input_path, pdf)

                    start = time.perf_counter()

                    try:
                        images = renderer.render_pdf(
                            pdf_path, self.imagemagick_convert_path, dpi=self.dpi)
                    except Exception as e:
                        errorMessage += " [{}]: {}".format(name, "Image Error")
                        self.__logError("{}|{}".format(self.directory, name), e)
                        continue

                    if self.__convert_pdf_to_html(xpdf_output_path_prefix, pdf, pdf_path):
                        if self.__process_figures(images, _input_path, pdf, xpdf_output_path_prefix, _output_path):
                            success += 1
                        else:
                            errorMessage += " [{}]: {}".format(name, "Zero Images or Error extraction of figures")
                            self.__logError("{}|{}".format(self.directory, name), "error extraction of figures")
                    else:
                        errorMessage += " [{}]: {}".format(name, "error Convert to HTML")
                        self.__logError("{}|{}".format(self.directory, name), "error Convert to HTML")
                    
                    end = time.perf_counter()
        
        if(success == total_pdf):
            status = "S"
            errorMessage = "Ok"
        else:
            if(success >= 1):
                status = "S"
                errorMessage = "Not all pdfs transformed, {}/{} success.".format(success, total_pdf) + errorMessage
            else:
                status = "E"
        # status = "S"
        # if(len(errorMessage)==0):
        #     errorMessage = 'Ok'
        # else:
        #     status = "E"
        self.__track(self.directory, status , errorMessage)  

        self.log_file.close()
        return len(files), total_pdf, success

    def __convert_pdf_to_html(self, _xpdf_output_path, _pdf, _pdf_path):
        try:
            # This variable seems to be hardcoded figures_caption_list
            xpdf_pdf_path = _xpdf_output_path + _pdf[:-4]

            if not isdir(xpdf_pdf_path):
                # check the execution of the pdftohtml binary of xpdf
                std_out = subprocess.check_output(
                    [self.xpdf_pdftohtml_path, _pdf_path, xpdf_pdf_path])

            return True
        except Exception as e:
            print("\nWrong %s\n" % _pdf)
            self.log_file.write("%s\n%s\n" % (_pdf, e))
            self.__logError(_pdf, e)
            return False

    def py2_wrapper(self, input_path, pdf, xpdf_output_path, chromedriver):
        # invoke python 2.7 (in Docker as python)
        gw = execnet.makegateway("popen//python=python")
        channel = gw.remote_exec("""
      import sys
      sys.path.append('/home/curation-pipeline/compiled')
      from xpdf_process import figures_captions_list
      channel.send(figures_captions_list(*channel.receive()))
    """)
        channel.send([input_path, pdf, xpdf_output_path, chromedriver])

        data = channel.receive()
        channel.waitclose()
        group = execnet.default_group
        group.terminate(timeout=1.0)

        return data

    def __extract_figures(self, _input_path, _pdf, _xpdf_output_path):
        # i don't get the logic behind wrong_count and flag.
        flag = 0
        wrong_count = 0
        figures = []
        info = None

        while flag == 0 and wrong_count < MAX_WRONG_COUNT:
            try:
                # process content using the ChromeDriver
                # figures, info = figures_captions_list(_input_path, _pdf, _xpdf_output_path, self.chrome_driver_path)
                figures, info = self.py2_wrapper(
                    _input_path, _pdf, _xpdf_output_path, self.chrome_driver_path)
                flag = 1
            except Exception as e:
                flag = 0
                wrong_count += 1
                time.sleep(5)
                # info['fig_no_est'] = 0
                print("error _extract_figures")
                self.log_file.write("%s\n%s" % (_pdf, e))
                self.__logError(_pdf, e)

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
        
        if len(figures)==0: # Zero images generated
            return False

        return True


    def __logTrack(self, _name, _output_path):
        time_string = time.strftime("%m/%d/%Y@%H:%M:%S", time.localtime())
        #message = "Successful" if _status == 'S' else "Error"
        #print(_name + message)
        record = _name + ", "+time_string #+ ", "+_status
        #tracker_path = join(_output_path, TRACK_FILE )
        os.system("echo '"+record+"' >> " + self.track_file)

    def __track(self, _id, _status, _message):
        record = _id + "|" + _status + "|" + _message
        print(record)
        os.system("echo '"+record+"' >> " + self.track_file)

    def __logError(self, _id, _error):
        record = _id + "|" + str(_error)
        print(record)
        os.system("echo '"+record+"' >> " + self.error_file)
    
    #Filter those already processed(tracker.csv) 
    # from the current list of files.
    def filterProcessed(self, _pdfList):
        df = pd.read_csv(self.track_file, delimiter='|', header=None)
        processed = df[df.iloc[:,1] == 'Sucess']      
        processed = processed.iloc[:,0].values.tolist()
        proc_pdf_list = [str(i)+".pdf" for i in processed]
        return list(set(_pdfList) - set(proc_pdf_list))