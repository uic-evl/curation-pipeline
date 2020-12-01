import execnet
import json
import subprocess
import time
import renderer

# from xpdf_process import figures_captions_list
from os import mkdir, listdir
from os.path import join, isdir
from pprint import pprint

PDF_OUTPUT_FOLDER = 'xpdf_'
LOG_FILE = 'PDFigCapXlog.txt'
MAX_WRONG_COUNT = 5

class PDFigCapX():
  def __init__(self, _chrome_drive_path, _xpdf_pdftohtml_path, _imagemagick_convert_path):
    self.chrome_driver_path = _chrome_drive_path
    self.xpdf_pdftohtml_path = _xpdf_pdftohtml_path
    self.imagemagick_convert_path = _imagemagick_convert_path
    self.log_file = None


  def extract(self, _input_path, _output_path):
    xpdf_output_path_prefix = join(_output_path, PDF_OUTPUT_FOLDER)  #xpdf_path
    log_file_path = join(_output_path, LOG_FILE)
    self.log_file = open(log_file_path, 'w')

    # process each pdf file in the input folder
    files = listdir(_input_path)
    success = 0
    total_pdf = 0

    for pdf in files:
      if (pdf.endswith('.pdf') or pdf.endswith('.PDF')) and not pdf.startswith('._'):
        total_pdf += 1
        pdf_path = join(_input_path, pdf)
        images = renderer.render_pdf(pdf_path, self.imagemagick_convert_path)

        if self.__convert_pdf_to_html(xpdf_output_path_prefix, pdf, pdf_path):
          if self.__process_figures(images, _input_path, pdf, xpdf_output_path_prefix, _output_path):
            success += 1
    self.log_file.close()
    return len(files), total_pdf, success


  def __convert_pdf_to_html(self, _xpdf_output_path, _pdf, _pdf_path):
    try:
      ##xpdf_pdf_path = join(_xpdf_output_path, _pdf[:-4]) # not creating folder inside xpdf_output but as prefix
      xpdf_pdf_path = _xpdf_output_path + _pdf[:-4]   # This variable seems to be hardcoded figures_caption_list
      if not isdir(xpdf_pdf_path):
        # check the execution of the pdftohtml binary of xpdf
        std_out = subprocess.check_output([self.xpdf_pdftohtml_path, _pdf_path, xpdf_pdf_path])
      return True
    except Exception as e:
      print("\nWrong %s\n" % _pdf)
      self.log_file.write("%s\n%s\n" % (_pdf, e))
      return False


  def py2_wrapper(self, input_path, pdf, xpdf_output_path, chromedriver):
    print("calling wrapper")
    gw = execnet.makegateway("popen//python=python2") # env specific
    channel = gw.remote_exec("""
      import sys
      sys.path.append('/home/juan/projects/Curation-Pipeline/compiled')
      from xpdf_process import figures_captions_list
      channel.send(figures_captions_list(*channel.receive()))
    """)
    channel.send([input_path, pdf, xpdf_output_path, chromedriver])
    return channel.receive()


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
        output = self.py2_wrapper(_input_path, _pdf, _xpdf_output_path, self.chrome_driver_path)
        print(type(output))
        print(len(output))
        flag = 1
      except Exception as e:
        flag = 0
        wrong_count += 1
        time.sleep(5)
        # info['fig_no_est'] = 0
        print("error _extract_figures")
        self.log_file.write("%s\n%s" % (_pdf, e))

      return figures, info, flag


  def __process_figures(self, _images, _input_path, _pdf, _xpdf_output_path, _output_path):
    data = {}
    data[_pdf] = {
      'figures': [],
      'pages_annotated': []
    }

    figures, info, flag = self.__extract_figures(_input_path, _pdf, _xpdf_output_path)
    if flag == 0: # there was an error in the extraction
      return False


    data[_pdf]['fig_no'] = info['fig_no_est']
    # the output images and captions are stored in a folder with the pdf name
    output_file_path = join(_output_path, _pdf[:-4])
    if not isdir(output_file_path):
      mkdir(output_file_path)

    for figure in figures:
      page_no = int(figure[:-4][4:])
      page_fig= _images[page_no -1]
      rendered_size = page_fig.size

      bboxes = figures[figure]
      order_no = 0
      for bbox in bboxes:
          order_no = order_no + 1
          png_ratio = float(rendered_size[1])/info['page_height']

          if len(bbox[1])>0:
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
            caption_output_filepath = join(output_file_path, '%d_%d.txt' % (page_no, order_no))
            with open(caption_output_filepath, 'w') as capoutput:
              #print len(bbox[1][1])
              #print bbox[1][1]
              #capoutput.write(str(bbox[1][1]))
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
          fig_extracted = page_fig.crop([int(bbox[0][0]*png_ratio), int(bbox[0][1]*png_ratio),
                          int((bbox[0][0]+bbox[0][2])*png_ratio), int((bbox[0][1]+bbox[0][3])*png_ratio)])
          fig_filepath = join(output_file_path, '%d_%d.jpg' % (page_no, order_no))
          fig_extracted.save(fig_filepath)

    json_file = join(output_file_path, '%s.json' % _pdf[:-4])
    with open(json_file, 'w') as outfile:
      json.dump(data[_pdf], outfile, ensure_ascii=False)
    return True
