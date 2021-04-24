import multiprocessing 
import time 
import subprocess
import sys
import math
import configparser
from configparser import ConfigParser, ExtendedInterpolation
import pandas as pd
from os.path import join, abspath, exists

config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
config.read('init.config')
extract_track_file = config['Image Extraction']['extract_track_file']

split_number_processors = config['Image Splitting']['split_number_processors']
split_track_file = config['Image Splitting']['split_track_file']
extract_ready_file = config['Image Splitting']['extract_ready_file']
reprocess_errors = config['Image Splitting']['split_reprocess_errors']
split_page_size = config['Image Splitting']['split_page_size']
split_page_size=int(split_page_size)

MAX_CPU = multiprocessing.cpu_count()

class Process(multiprocessing.Process): 
    def __init__(self, _id, _page_size, _file_path): 
        #Process(i, page_size, file_path) 
        super(Process, self).__init__() 
        self.id = _id
        self.page_size = _page_size
        self.file_path = _file_path
        
    def run(self): 
        print("running sub process: " + str(self.id))
        cmd = "python3 Split.py {} {} {} ".format(str(self.file_path), str(self.page_size), str(self.id)) 
        subprocess.call(cmd, shell=True)
  
if __name__ == '__main__': 

    df_extract_track = pd.read_csv(extract_track_file, header=None, sep='|', usecols=[0,1])
    df_extract_track = df_extract_track[df_extract_track[1]=='S'][0]
    df_extract_track.to_csv(extract_ready_file, index = False, header=None) 
    total_rows = df_extract_track.shape[0]

    if exists(split_track_file):
        df_split_track = pd.read_csv(split_track_file, header=None, sep='|', usecols=[0,1])
        # if(reprocess_errors=='yes'):
        #     df_split_track = df_split_track[df_split_track[1]=='S']
        count_split_track = df_split_track.shape[0]

        if count_split_track>0:
            #get difference
            newdf = df_extract_track[~df_extract_track.isin(df_split_track[0])]
            #store the new delta difference in the file
            newdf.to_csv(extract_ready_file, index = False, header=None) 
            # new total to split
            total_rows = newdf.shape[0]


    split_number_processors = int(split_number_processors)
    
    #customized page size or taking whole file
    if(split_page_size!=0):
        page_size = split_page_size
    else:
        page_size = math.ceil(total_rows / split_number_processors)


    for i in range(1, split_number_processors+1):
        p = Process(i, page_size, extract_ready_file) 
        p.start()
   