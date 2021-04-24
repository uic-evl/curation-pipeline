import sys
import os
from os.path import join, abspath,isdir, exists
import time
from pathlib import Path
import pandas as pd

#Arguments
file_path = sys.argv[1]
page_size = int(sys.argv[2])
offset = int(sys.argv[3])

#paths
current_dir = os.getcwd()
source_dir = abspath(join(current_dir, '..'))
sys.path.append(source_dir)
project_dir = abspath(join(source_dir,'..'))
input_path =  abspath(join(project_dir, 'input'))
# output_path = abspath(join(project_dir, 'output')) 
# log_path = abspath(join(project_dir, 'log')) 
output_path = "/mnt/collection1015/output"
log_path = "/mnt/collection1015/log"

#Log files
LOG_FILE = "download"+str(offset)+".log"
LOG_PATH = join(log_path, LOG_FILE)
if not exists(LOG_PATH):
    Path(LOG_PATH).touch()

def __log(_msg):
    record = str(offset)+"  "+ str(_msg)
    print(record)
    os.system("echo '"+record+"' >> " + LOG_PATH)

def getRange(_df):
    if (offset == 1):
        start = 0
    else:
        start = (page_size * (offset-1))
    
    end = (page_size * offset)
    if( end > _df.shape[0]):
        end = _df.shape[0]
        
    return start, end

def getList():
    df = pd.read_csv(file_path)
    start, end = getRange(df)
    __log("Range: " + str(start)+" "+ str(end))
    df = df[start:end]['pmcid']
    return df.tolist()

pmcids = getList()

from DownloadPaper import DownloadPaper
dp = DownloadPaper(output_path, log_path)

count_download = 0
total_time = 0
total_docs = len(pmcids)

for id in pmcids:
    ftp_url, error = dp.get_targz_location(id)
    if not error:
        
        __log("Downloading: " + id)

        start = time.perf_counter()
        
        dp.download_and_extract(ftp_url, id)
        
        end = time.perf_counter()
        unit_time = end - start
        unit_time = round(unit_time, 3)
        total_time = total_time + unit_time
        total_time = round(total_time, 3)
        
    else:
        __log('Error: {0} - {1}'.format(id, ftp_url if not error else error))
    
    count_download +=1
    time_string = time.strftime("%H:%M:%S %m/%d/%Y", time.localtime())
    __log("{} completed. Time:{} | Total Time:{} | Total {} out of {} in this set | at {}"
    .format(id,unit_time, total_time,count_download, total_docs, time_string))

__log("Process Completed.")