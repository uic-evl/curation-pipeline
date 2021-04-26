import sys
from os import getcwd, mkdir, listdir, remove
from os.path import abspath, join, isdir
import time

current_dir = getcwd()
source_dir = abspath(join(current_dir, '..'))
sys.path.append(source_dir)

project_dir = abspath(join(source_dir,'..'))
log_path =  abspath(join(project_dir, 'log'))
input_path =  abspath(join(project_dir, 'output'))
output_path = abspath(join(project_dir, 'output')) 
log_path = abspath(join(project_dir, 'log')) 

print("Reading from: "+ input_path)

from FigSplitWrapper import FigSplitWrapper
FIGSPLIT_URL = 'https://www.eecis.udel.edu/~compbio/FigSplit'
fsw = FigSplitWrapper(FIGSPLIT_URL)

start_total = time.perf_counter()
main_directories = [ name for name in listdir(input_path) if isdir(join(input_path, name)) ]

for main_dir in main_directories:
      print("Dir: " + main_dir)
      main_dir = join(output_path, main_dir)

      #Iteration in case there were more than one pdf extracted (extras, apendix, etc)
      sub_directories = [ name for name in listdir(main_dir) if isdir(join(main_dir, name)) ]
      for sub_dir in sub_directories:
            ## if start with xpdf_ do not consider
            if not sub_dir.startswith( 'xpdf_' ):
                  start = time.perf_counter()
                  print("\tSub-dir source: " + sub_dir)
                  name = 'figsplit_'+sub_dir
                  sub_dir = join(main_dir, sub_dir)
                  new_output_dir = join(main_dir, name)
                  if not isdir(new_output_dir):
                        mkdir(new_output_dir)
                  print("\tSub-dir output: " + name)

                  total_figures, total_figures_splitted = fsw.split(sub_dir, new_output_dir, log_path)
                  if len(new_output_dir) == 0:
                        remove(new_output_dir)

                  print("\n\tTotal Figures: %d\n\tTotal splitted: %d" %(total_figures, total_figures_splitted))
                  end = time.perf_counter()
                  taken_time = end - start
                  taken_time = round(taken_time, 3)
                  print("\ttime: " + str(taken_time))
            ##

end_total = time.perf_counter()
total_time = end_total - start_total
total_time = round(total_time, 3)
print("\nTotal Time: " + str(total_time))