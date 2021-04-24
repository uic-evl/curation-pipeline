import sys
import os
import time
from os.path import join, abspath,isdir, exists
from pathlib import Path

current_dir = os.getcwd()
source_dir = abspath(join(current_dir, '..'))
sys.path.append(source_dir)
project_dir = abspath(join(source_dir,'..'))

input_path =  abspath(join(project_dir, 'input'))
output_path = abspath(join(project_dir, 'output')) 
log_path = abspath(join(project_dir, 'log')) 

print("input: " + input_path)
print("output: " + output_path)

#Log files
LOG_FILE = "download.log"
LOG_PATH = join(log_path, LOG_FILE)
if not exists(LOG_PATH):
    Path(LOG_PATH).touch()

def __log(_msg):
    record = str(_msg)
    print(record)
    os.system("echo '"+record+"' >> " + LOG_PATH)

pmcids = ['PMC212776','PMC2762542', 'PMC7124120']
#ids = [line.strip() for line in open("pmcids.csv", 'r')]

from DownloadPaper import DownloadPaper
dp = DownloadPaper(output_path, log_path)

count_download = 0
total_time = 0
total_docs = len(pmcids)

for id in pmcids:
    __log("Scanning: " + id)
    start = time.perf_counter()
    
    ftp_url, error = dp.get_targz_location(id)
    if not error:
        dp.download_and_extract(ftp_url, id)    
    else:
        __log('Error: {0} - {1}'.format(id, ftp_url if not error else error))

    end = time.perf_counter()
    unit_time = end - start
    unit_time = round(unit_time, 3)
    total_time = total_time + unit_time
    total_time = round(total_time, 3)

    count_download +=1
    time_string = time.strftime("%H:%M:%S %m/%d/%Y", time.localtime())
    __log("{} completed. Time:{} | Total Time:{} | Total {} out of {} in this set | at {}"
    .format(id,unit_time, total_time,count_download, total_docs, time_string))

__log("Process Completed.")