import sys
from os import getcwd
from os.path import join, abspath

current_folder = getcwd()
source_folder = abspath(join(current_folder, '..'))
sys.path.append(source_folder)

from PDFigCapX import PDFigCapX

# windows
#dependecies_folder = abspath(join(current_folder, '..', '..', 'dependencies', 'win'))
#chrome_driver_path = join(dependecies_folder, 'chromedriver_win32','chromedriver.exe')
#xpdf_pdftohtml_path = join(dependecies_folder, 'xpdf', 'bin64', 'pdftohtml.exe')
#imagemagick_convert_path = join(dependecies_folder, 'ImageMagick-7.0.8-26-portable-Q16-x86', 'convert.exe')

# mac
dependecies_folder = abspath(join(current_folder, '..', '..', 'dependencies', 'mac'))
chrome_driver_path = join(dependecies_folder,'chromedriver')
xpdf_pdftohtml_path = join(dependecies_folder, 'xpdf-tools-mac-4.00', 'bin64', 'pdftohtml')
imagemagick_convert_path = join(dependecies_folder, 'ImageMagick-7.0.8', 'bin', 'convert')

input_path = abspath(join(current_folder, '..', '..', 'input'))
output_path = abspath(join(current_folder, '..', '..', 'output'))

p = PDFigCapX(chrome_driver_path, xpdf_pdftohtml_path, imagemagick_convert_path)
total_files, total_pdf, total_successes = p.extract(input_path, output_path)

print "Total files: %d\nTotal PDFs: %d\nTotal successes: %d" % (total_files, total_pdf, total_successes)
