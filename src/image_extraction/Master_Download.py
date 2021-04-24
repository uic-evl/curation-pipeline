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

pmcid_file = config['DEFAULT']['pmcid_file']
delta_diff_file = config['DEFAULT']['delta_diff_file']
num_processors = config['Download']['download_number_processors']
download_track_file = config['Download']['download_track_file']

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
        cmd = "python3 Download.py {} {} {} ".format(str(self.file_path), str(self.page_size), str(self.id)) 
        subprocess.call(cmd, shell=True)
  
if __name__ == '__main__': 

    #Validate if there exist documents already procssed (compare with track)
    df_pmcid = pd.read_csv(pmcid_file, usecols=['pmcid'])
    total_rows = df_pmcid.shape[0] 
    
    if exists(download_track_file):
        df_track = pd.read_csv(download_track_file, header=None, sep='|', usecols=[0])
        track_count = df_track.shape[0]

        if track_count>0:
            #get difference
            newdf = df_pmcid[~df_pmcid.pmcid.isin(df_track[0])]
            #new file to store the new delta difference
            newdf.to_csv (delta_diff_file, index = False) 
            #consider the new delta difference as the input of pmcids
            pmcid_file = delta_diff_file
            # new total to split
            total_rows = newdf.shape[0]

    num_processors = int(num_processors)
        
    print("Total rows {}".format(total_rows))
    print("Num Processors: {}".format(num_processors))
    page_size = math.ceil(total_rows / num_processors)
    print("Page size: {}".format(page_size))

    for i in range(1, num_processors+1):
        p = Process(i, page_size, pmcid_file) 
        p.start()
