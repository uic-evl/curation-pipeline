from PDFigCapX import PDFigCapX
from os import getcwd
from os.path import join

current_folder = getcwd()
chrome_driver_path = join(current_folder, 'chromedriver_win32','chromedriver.exe')
xpdf_pdftohtml_path = join(current_folder, 'xpdf', 'bin64', 'pdftohtml.exe')
imagemagick_convert_path = join(current_folder, 'ImageMagick-7.0.8-26-portable-Q16-x86', 'convert.exe')
input_path = join(current_folder, 'sample_data_for_Juan')
output_path = join(current_folder, 'output')

p = PDFigCapX(chrome_driver_path, xpdf_pdftohtml_path, imagemagick_convert_path)
total_files, total_pdf, total_successes = p.extract(input_path, output_path)

print "Total files: %d\nTotal PDFs: %d\nTotal successes: %d" % (total_files, total_pdf, total_successes)