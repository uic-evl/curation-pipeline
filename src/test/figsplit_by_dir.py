import sys
import os
from os import getcwd, mkdir, listdir, remove
from os.path import abspath, join, isdir, exists
import time
from pathlib import Path
import pandas as pd

#Arguments
file_path = sys.argv[1]
page_size = int(sys.argv[2])
offset = int(sys.argv[3])

#paths
#input_path =  '/Users/Gustavo/Documents/597_Project/Allen-Collection-Curation/output/pos_neg/output_pos_neg'
input_path = '/mnt/wormbase_output'
output_path = input_path
# log_path = '/Users/Gustavo/Documents/597_Project/Allen-Collection-Curation/output/pos_neg/log'
log_path = '/mnt/wormbase_log'


#Log files
LOG_FILE = "split"+str(offset)+".log"
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
    df = pd.read_csv(file_path, delimiter='|', header=None)
    start, end = getRange(df)
    df = df[start:end]
    proccessed = df[(df.iloc[:,1] == 'Sucess') | (df.iloc[:,1] == 'Success')]
    return proccessed[0].tolist()

#work over a portion of the main file
# df = pd.read_csv(file_path, header=None)
# start, end = getRange()
# directories = df[start:end][0].tolist()
directories = getList()
print(directories)

current_dir = getcwd()
source_dir = abspath(join(current_dir, '..'))
sys.path.append(source_dir)
project_dir = abspath(join(source_dir,'..'))



from FigSplitWrapper import FigSplitWrapper
FIGSPLIT_URL = 'https://www.eecis.udel.edu/~compbio/FigSplit'
fsw = FigSplitWrapper(FIGSPLIT_URL)

count = 0
total_time = 0

for directory in directories:

    fullpath_dir = join(input_path, directory)
    if not isdir(fullpath_dir):
        __log("{} - does not exist, skipped.".format(directory))
        continue
    
    __log("{} started.".format(directory))

    new_dir_name = 'figsplit_'+directory
    new_fullpath_dir =  join(fullpath_dir, new_dir_name)
    if not isdir(new_fullpath_dir):
        mkdir(new_fullpath_dir)

    unit_start=time.perf_counter()

    total_figures, total_figures_splitted = fsw.split(
            fullpath_dir, new_fullpath_dir, log_path, directory)

    unit_end=time.perf_counter()
    unit_time = unit_end - unit_start                  
    unit_time = round(unit_time, 3)

    total_time = total_time + unit_time
    total_time = round(total_time, 3)

    if len(new_fullpath_dir) == 0:
        remove(new_fullpath_dir)
        __log("{} - Generated no files".format(directory))

    count += 1
    time_string = time.strftime("%H:%M:%S %m/%d/%Y", time.localtime())
    __log("{} completed. Time:{} | Figures:{} | Splitted:{} || Total Time:{} | Total directories:{} | at {}"
    .format(directory,unit_time,total_figures, total_figures_splitted, total_time, count, time_string))

__log("Process Completed.")