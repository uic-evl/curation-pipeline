import sys
from os import getcwd
from os.path import join, abspath

current_folder = getcwd()
source_folder = abspath(join(current_folder, '..'))
sys.path.append(source_folder)
from PDFigCapX import PDFigCapX

chrome_driver_path = join('/usr/bin/chromedriver')
xpdf_pdftohtml_path = "/usr/local/bin/pdftohtml"

input_path = abspath(join(current_folder, '..', '..', 'input'))
output_path = '/mnt/output'

p = PDFigCapX(_chrome_drive_path=chrome_driver_path,
              _xpdf_pdftohtml_path=xpdf_pdftohtml_path)
total_files, total_pdf, total_successes = p.extract(input_path, output_path)

print("Total files: %d\nTotal PDFs: %d\nTotal successes: %d" %
      (total_files, total_pdf, total_successes))
