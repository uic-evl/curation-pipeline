import sys
from os import getcwd, mkdir, listdir, remove
from os.path import abspath, join, isdir, exists
import time
from pathlib import Path

#arguments
processID = '0' if len(sys.argv) < 2 else str(sys.argv[1])

current_dir = getcwd()
source_dir = abspath(join(current_dir, '..'))
sys.path.append(source_dir)
project_dir = abspath(join(source_dir,'..'))

input_path =  abspath(join(source_dir, 'preprocessing', 'split' ))
output_path = abspath(join(project_dir, 'output')) 
log_path = abspath(join(project_dir, 'log')) 

TRACK_FILE = "split_track"+str(processID)+".csv"
TRACK_PATH = join(log_path, TRACK_FILE)

LOG_FILE = "split"+str(processID)+".log"
LOG_PATH = join(log_path, LOG_FILE)

if not exists(TRACK_PATH):
    Path(TRACK_PATH).touch()

if not exists(LOG_PATH):
    Path(LOG_PATH).touch()

file_name = 'file'+str(processID)+'.csv'
pmcid_file = join(input_path, file_name)

with open(pmcid_file,'r') as f:
    pmcid_list = set(pmcid.strip() for pmcid in f)

def log(data):
    data = str(processID)+": " + str(data)
    with open(LOG_PATH, 'a') as log_file:
        log_file.write(data+"\n")   
    print(data)

def track_pmcid(pmcid):
    with open(TRACK_PATH, 'a') as track_file:
        track_file.write(pmcid+'\n')


from FigSplitWrapper import FigSplitWrapper
FIGSPLIT_URL = 'https://www.eecis.udel.edu/~compbio/FigSplit'
fsw = FigSplitWrapper(FIGSPLIT_URL)

total_time = 0
dir_count = 0

for pmcid in pmcid_list:
    log(str(pmcid)+" begins:")
    pmc_dir =  abspath(join(output_path,pmcid))
    if not exists(pmc_dir):
        log("\t"+pmc_dir+" does not exist, skipped.")
        continue

    #Iteration in case there were more than one pdf extracted (extras, apendix, etc)
    ## if start with xpdf_ do not consider
    sub_directories = [ name for name in listdir(pmc_dir) if isdir(join(pmc_dir, name)) and not name.startswith('xpdf_') ]
    if(len(sub_directories)==0):
        log("\t"+pmc_dir+" no diretories other than xpdf_* , skipped.")
        continue
      
    for sub_dir in sub_directories:
        
        sub_dir_name = sub_dir
        name = 'figsplit_'+sub_dir
        sub_dir = join(pmc_dir, sub_dir)
        new_output_dir = join(pmc_dir, name)
        if not isdir(new_output_dir):
            mkdir(new_output_dir)

        unit_start=time.perf_counter()

        total_figures, total_figures_splitted = fsw.split(
            sub_dir, new_output_dir, log_path, pmcid)

        unit_end=time.perf_counter()
        unit_time = unit_end - unit_start                  
        unit_time = round(unit_time, 3)
        total_time = total_time + unit_time
        total_time = round(total_time, 3)

        if len(new_output_dir) == 0:
            remove(new_output_dir)
            log("\t{}/{} - Generated no files".format(pmcid, sub_dir_name))
        else:
            log("\t{}/{} - Time:{} | Figures:{} | Splitted:{}"
            .format(pmcid,sub_dir_name,unit_time, total_figures, total_figures_splitted ))
                        
    track_pmcid(pmcid)
    dir_count += 1
    time_string = time.strftime("%H:%M:%S %m/%d/%Y", time.localtime())
    log("\t{} completed. Total PMCIDs:{} | Total time:{} | at {}"
    .format(pmcid,dir_count, total_time, time_string))

log("Process Completed.")