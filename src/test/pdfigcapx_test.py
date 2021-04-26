import sys
import os
from os.path import join, abspath, exists
from os import mkdir, listdir
import subprocess
import time

current_dir = os.getcwd()
source_dir = abspath(join(current_dir, '..'))
sys.path.append(source_dir)
project_dir = abspath(join(source_dir,'..'))

#output of previous process becomes input of this one.
input_path =  abspath(join(project_dir, 'output'))
output_path = abspath(join(project_dir, 'output')) 
log_path = abspath(join(project_dir, 'log')) 

TRACK_FILE_NAME = "pdf_tracker.csv"
TRACK_FILE_PATH = join(log_path, TRACK_FILE_NAME)

#if not exists(TRACK_FILE_PATH):
    #create

print("Reading from: "+input_path)
#files = listdir(input_path) # ToDo: take time
directories = [ name for name in os.listdir(input_path) if os.path.isdir(os.path.join(input_path, name)) ]
# print(directories)

chrome_driver_path = join('/usr/bin/chromedriver')
xpdf_pdftohtml_path = "/usr/local/bin/pdftohtml"

from PDFigCapX import PDFigCapX
p = PDFigCapX(_chrome_drive_path=chrome_driver_path,
              _xpdf_pdftohtml_path=xpdf_pdftohtml_path)


all_set = set(directories) # ToDo: take time
files_count = len ( all_set )
track_count = 0

print(all_set)
print(TRACK_FILE_PATH)

start_total = time.perf_counter()

while (all_set):
    #Based on tracker file create a set, keep counter.
    trackerSet  = set(line.strip() for line in open( TRACK_FILE_PATH ))
    #print("tracker set: "+ str(trackerSet))
    track_count = len(trackerSet)   
    if track_count >= files_count:
        break

    start = time.perf_counter()
    #Get pending records to processs and get one
    all_set.difference_update( trackerSet )
    selected =  all_set.pop()

    #Add selected one to the tracker file
    print("selected: " + selected)
    subprocess.Popen("echo '"+selected+"' >> "+TRACK_FILE_PATH, shell=True)
    #print("directory: " + selected)
    input_dir = abspath(join(input_path, selected))    
    output_path = input_dir   
    total_files, total_pdf, total_successes = p.extract(input_dir, output_path, log_path)
    end = time.perf_counter()
    taken_time = end - start
    taken_time = round(taken_time, 3)
    print("\ttime: " + str(taken_time))
    print("# docs processed: " + str(track_count))

end_total = time.perf_counter()
total_time = end_total - start_total
total_time = round(total_time, 3)
print("\nTotal Time: " + str(total_time))
'''
for directory in directories:
    print("directory: " + directory)
    input_dir = abspath(join(input_path, directory))    
    output_path = input_dir   
    total_files, total_pdf, total_successes = p.extract(input_dir, output_path, log_path)
'''
#print("Total files: %d\nTotal PDFs: %d\nTotal successes: %d" %
#      (total_files, total_pdf, total_successes))
