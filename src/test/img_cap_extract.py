import sys
import os
from os.path import join, abspath, exists
from os import mkdir, listdir
import subprocess
import time
from pathlib import Path

#from filelock import FileLock
#from filelock import FileLock
# from test.filelock import FileLock
#from filelock import FileLock

#from lockfile import LockFile



processID = 'P0' if len(sys.argv) < 2 else 'P'+str(sys.argv[1])

def log(data):
    data = processID+": " + str(data)
    with open(TRACK_LOG_PATH, 'w') as log_file:
        log_file.write(data)
    #subprocess.call("echo '"+data+"' >> "+TRACK_LOG_PATH, shell=True)
    print(data)

import fcntl #file control module

def getPMCID(_file_path):
    pmcID = 0
    end_of_file = False
    trackerSet = set()
    tracker_count = 0
    while True:
        try:
            with open(_file_path,'r+') as tracker_file: 
                #lock the file                  
                fcntl.flock(tracker_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
             
                trackerSet = set(pmcid.strip() for pmcid in tracker_file)
                tracker_count = len(trackerSet) 
                
                if tracker_count >= initial_dir_count:
                    end_of_file = True
                    break

                #Get pending records to processs and get one
                all_set.difference_update( trackerSet )
                pmcID =  all_set.pop()

                #Add selected one to the tracker file
                tracker_file.write(pmcID+'\n')

                #and now unlock it so other processed can edit it!           
                fcntl.flock(tracker_file, fcntl.LOCK_UN)
                break 
        except OSError as e:
            log("Exception: " + str(e))
            time.sleep(0.05) #wait before retrying 

    return pmcID, end_of_file, tracker_count


current_dir = os.getcwd()
source_dir = abspath(join(current_dir, '..'))
sys.path.append(source_dir)
project_dir = abspath(join(source_dir,'..'))

#output of previous process becomes input of this one.
input_path =  abspath(join(project_dir, 'output'))
output_path = abspath(join(project_dir, 'output')) 
log_path = abspath(join(project_dir, 'log')) 

TRACK_FILE_NAME = "xpdf_track.csv"
TRACK_FILE_PATH = join(log_path, TRACK_FILE_NAME)

TRACK_LOG_FILE = "xpdf.log"
TRACK_LOG_PATH = join(log_path, TRACK_LOG_FILE)


if not exists(TRACK_FILE_PATH):
    Path(TRACK_FILE_PATH).touch()

if not exists(TRACK_LOG_PATH):
    Path(TRACK_LOG_PATH).touch()


directories = [ name for name in os.listdir(input_path) if os.path.isdir(os.path.join(input_path, name)) ]
chrome_driver_path = join('/usr/bin/chromedriver')
xpdf_pdftohtml_path = "/usr/local/bin/pdftohtml"

from PDFigCapX import PDFigCapX
p = PDFigCapX(_chrome_drive_path=chrome_driver_path,
              _xpdf_pdftohtml_path=xpdf_pdftohtml_path)

all_set = set(directories) # ToDo: take time
initial_dir_count = len ( all_set )
tracker_count = 0
docs_processed = 0

start_total = time.perf_counter()
total_time = 0

while (all_set):
    start = time.perf_counter()

    selected, end_file, tracker_count = getPMCID(TRACK_FILE_PATH)
    if end_file:
        break
    log("Processing: " + selected)
    
    input_dir = abspath(join(input_path, selected))    
    output_path = input_dir   
    
    total_files, total_pdf, total_successes = p.extract(input_dir, output_path, log_path, False)
    
    end = time.perf_counter()
    docs_processed += 1
    taken_time = end - start
    taken_time = round(taken_time, 3)
    total_time = total_time + taken_time
    total_time = round(total_time,3)
    docs_processed # documents completed in this process
    tracker_count +=1  # Total documents in the tracker (considering other processes)
    time_string = time.strftime("%H:%M:%S %m/%d/%Y", time.localtime())
    log("\tTime: {} | Total time: {} | #docs: {} | #Total docs: {} | at {}".format(taken_time, total_time, docs_processed, tracker_count, time_string ))

log("Completed.")


