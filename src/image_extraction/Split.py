import sys
import os
from os import getcwd, mkdir, listdir, remove, rmdir
from os.path import abspath, join, isdir, exists
import time
from pathlib import Path
import pandas as pd
import configparser
from configparser import ConfigParser, ExtendedInterpolation

config = configparser.ConfigParser(interpolation=ExtendedInterpolation())

config.read('init.config')
output_path = config['DEFAULT']['output_dir']
log_path = config['DEFAULT']['log_dir']
input_path =output_path
split_track_file = config['Image Splitting']['split_track_file']

#Arguments
file_path = sys.argv[1]
page_size = int(sys.argv[2])
offset = int(sys.argv[3])

#Log files
LOG_FILE = "split"+str(offset)+".log"
LOG_PATH = join(log_path, LOG_FILE)
if not exists(LOG_PATH):
    Path(LOG_PATH).touch()

def __log(_msg):
    record = str(offset)+"  "+ str(_msg)
    print(record)
    os.system("echo '"+record+"' >> " + LOG_PATH)

def __track(_id, _status, _message):
    record = _id + "|" + _status + "|" + _message
    os.system("echo '"+record+"' >> " + split_track_file)

def getRange(_total_count):
    if (offset == 1):
        start = 0
    else:
        start = (page_size * (offset-1))
    
    end = (page_size * offset)
    if( end > _total_count):
        end = _total_count
        
    return start, end

def getList():
    df = pd.read_csv(file_path, header=None)
    start, end = getRange(df.shape[0])
    __log("Range: " + str(start)+" "+ str(end))
    df = df[start:end]
    return df[0].tolist()

directories = getList()

current_dir = getcwd()
source_dir = abspath(join(current_dir, '..'))
sys.path.append(source_dir)
project_dir = abspath(join(source_dir,'..'))


from FigSplitWrapper import FigSplitWrapper
FIGSPLIT_URL = 'https://www.eecis.udel.edu/~compbio/FigSplit'
fsw = FigSplitWrapper(FIGSPLIT_URL)

count = 0
total_time = 0
total_documents = len(directories)

for directory in directories:
    __log("{} scanning.".format(directory))

    fullpath_dir = join(input_path, directory)
    if not isdir(fullpath_dir):
        __track(directory, 'E', 'Diretory does not exist')
        __log("{} - does not exist, skipped.".format(directory))
        continue
    
    #Iteration in case more than one pdf extracted (extras, apendix, etc)
    # if start with xpdf_ do not consider
    sub_directories = [ name for name in listdir(fullpath_dir) if isdir(join(fullpath_dir, name)) and not name.startswith('xpdf_') ]
    if(len(sub_directories)==0):
        __track(directory, 'E', 'no diretories other than xpdf_')
        __log("\t{} no diretories other than xpdf_* , skipped.".format(directory))
        continue
    unit_start=time.perf_counter()
    detail_msg = ''
    success = 0

    for sub_dir in sub_directories:
        new_subdir_name = 'figsplit_'+sub_dir
        new_fullpath_dir =  join(fullpath_dir, new_subdir_name)
        full_subdir = join(fullpath_dir, sub_dir)

        if not isdir(new_fullpath_dir):
            mkdir(new_fullpath_dir)
                
        total_figures, total_figures_splitted, msg = fsw.split(
                full_subdir, new_fullpath_dir, log_path, directory)
        detail_msg += msg

        if(total_figures ==0 or total_figures_splitted == 0):
            detail_msg += " [{}] No images splited.".format(sub_dir) 
        else:
            success += 1

        if len(listdir(new_fullpath_dir)) == 0:
            #rmdir(new_fullpath_dir)
            detail_msg += ' empty split_ folder.'
            __log("\t{}/{} - Generated no files".format(directory, sub_dir))
        else:
            __log("\t{}/{} - Figures:{} | Splitted:{}"
            .format(directory,sub_dir,total_figures, total_figures_splitted ))

    status = 'S'
    if(len(detail_msg)==0):
        detail_msg = 'Ok'
    else:
        if ("500" in detail_msg):
            detail_msg = 'Server error'
            status = 'E'
        elif("Unexpected" in detail_msg):
            detail_msg = 'Unexpected error'
            status = 'E'
    __track(directory, status, detail_msg)

    unit_end=time.perf_counter()
    unit_time = unit_end - unit_start                  
    unit_time = round(unit_time, 3)
    total_time = total_time + unit_time
    total_time = round(total_time, 3)
    count += 1
    time_string = time.strftime("%H:%M:%S %m/%d/%Y", time.localtime())

    __log("{} completed. Time:{} | Total Time:{} | {} items out of {} | at {}"
    .format(directory,unit_time,total_time, count,total_documents, time_string))

__log("Process Completed.")