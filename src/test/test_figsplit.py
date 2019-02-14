import sys
from os import getcwd
from os.path import abspath, join

current_folder = getcwd()
source_folder = abspath(join(current_folder, '..'))
sys.path.append(source_folder)

from FigSplitWrapper import FigSplitWrapper

output_folder = abspath(join(current_folder, '..', '..', 'output'))
input_folder_path = join(output_folder, '23949442')

FIGSPLIT_URL = 'https://www.eecis.udel.edu/~compbio/FigSplit'
fsw = FigSplitWrapper(FIGSPLIT_URL)

total_figures, total_figures_splitted = fsw.split(input_folder_path)
print "\nTotal Figures: %d\nTotal splitted: %d" % (total_figures, total_figures_splitted)