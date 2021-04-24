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
download_track_file = config['Download']['download_track_file']
extract_number_processors = config['Image Extraction']['extract_number_processors']
extract_track_file = config['Image Extraction']['extract_track_file']
download_ready_file = config['Image Extraction']['download_ready_file']
extract_page_size = config['Image Extraction']['extract_page_size']
extract_page_size=int(extract_page_size)

MAX_CPU = multiprocessing.cpu_count()

class Process(multiprocessing.Process): 
    def __init__(self, _id, _page_size, _download_ready_file): 
        super(Process, self).__init__() 
        self.id = _id
        self.page_size = _page_size
        self.file_path = _download_ready_file
        
    def run(self): 
        print("running sub process: " + str(self.id))
        cmd = "python3 Extract.py {} {} {} ".format(str(self.file_path), str(self.page_size), str(self.id)) 
        print(cmd)
        subprocess.call(cmd, shell=True)
  
if __name__ == '__main__': 

    if len(sys.argv) < 2:
        processor_number = 1
    else:
        processor_number = int(sys.argv[1])
        if (processor_number >= MAX_CPU):
            print("Cannot reach the max of CPU: " + str(MAX_CPU))
            sys.exit()


    df_download_track = pd.read_csv(download_track_file, header=None, sep='|', usecols=[0,1])
    df_download_track = df_download_track[df_download_track[1]=='S'][0]
    df_download_track.to_csv(download_ready_file, index = False, header=None) 
    total_rows = df_download_track.shape[0]

    if exists(extract_track_file):
        df_extract_track = pd.read_csv(extract_track_file, header=None, sep='|', usecols=[0,1])
        count_extract_track = df_extract_track.shape[0]

        if count_extract_track>0:
            #get difference
            newdf = df_download_track[~df_download_track.isin(df_extract_track[0])]
            #store the new delta difference in the file
            newdf.to_csv(download_ready_file, index = False, header=None) 
            # new total to split
            total_rows = newdf.shape[0]


    extract_number_processors = int(extract_number_processors)
    print("Total rows {}".format(total_rows))
    print("Num Processors: {}".format(extract_number_processors))

    if(extract_page_size!=0):
        page_size = extract_page_size
    else:
        page_size = math.ceil(total_rows / extract_number_processors)

    print("Page size: {}".format(page_size))

    for i in range(1, extract_number_processors+1):
        p = Process(i, page_size, download_ready_file) 
        p.start()