import sys
from os import getcwd
from os.path import join, abspath, exists

current_folder = getcwd()
source_folder = abspath(join(current_folder, '..'))
sys.path.append(source_folder)

from Pipeline import Pipeline

dependecies_folder = abspath(join(current_folder, '..', '..', 'dependencies', 'mac'))
chromedriver_path = join(dependecies_folder,'chromedriver')
xpdf_pdftohtml_path = join(dependecies_folder, 'xpdf-tools-mac-4.00', 'bin64', 'pdftohtml')
imagemagick_convert_path = join(dependecies_folder, 'ImageMagick-7.0.8', 'bin', 'convert')
figsplit_url = 'https://www.eecis.udel.edu/~compbio/FigSplit'

config = {
    'chromedriver_path': chromedriver_path,
    'xpdf_pdftohtml_path': xpdf_pdftohtml_path,
    'imagemagick_convert_path': imagemagick_convert_path,
    'figsplit_url': figsplit_url
}

input_folder = abspath(join(current_folder, '..', '..', 'input'))
output_folder = abspath(join(current_folder, '..', '..', 'output'))
input_document_path = join(input_folder, '15350224.pdf')

p = Pipeline(config)
p.process_file(input_document_path, output_folder)
