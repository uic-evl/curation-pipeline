import sys
import os
from os.path import join, abspath, exists
from os import mkdir, listdir
import subprocess
import time
from pathlib import Path

import pandas as pd
import configparser
from configparser import ConfigParser, ExtendedInterpolation

config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
config.read('init.config')
output_path = config['DEFAULT']['output_dir']
log_path = config['DEFAULT']['log_dir']

#Arguments
file_path = sys.argv[1]
page_size = int(sys.argv[2])
offset = int(sys.argv[3])


#Log files
LOG_FILE = "extract"+str(offset)+".log"
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
    df = pd.read_csv(file_path, header=None)
    start, end = getRange(df)
    __log("Range: " + str(start)+" "+ str(end))
    df = df[start:end][0]
    return df.tolist()

pmcids = getList()

chrome_driver_path = join('/usr/bin/chromedriver')
xpdf_pdftohtml_path = "/usr/local/bin/pdftohtml"

current_dir = os.getcwd()
source_dir = abspath(join(current_dir, '..'))
sys.path.append(source_dir)

from PDFigCapX import PDFigCapX
p = PDFigCapX(_chrome_drive_path=chrome_driver_path,
              _xpdf_pdftohtml_path=xpdf_pdftohtml_path)

total_time = 0
counter = 0
total_documents = len(pmcids)

for id in pmcids:
    start = time.perf_counter()

    input_path = abspath(join(output_path, id))    
    total_files, total_pdf, total_successes = p.extract(
        input_path, input_path, log_path, False)

    end = time.perf_counter()
    unit_time = end - start
    unit_time = round(unit_time, 3)
    total_time += unit_time
    counter += 1
    total_time = round(total_time,3)
    time_string = time.strftime("%H:%M:%S %m/%d/%Y", time.localtime())
    record = "{}\tTime: {} | Total time: {} | {} items out of {} | at {}".format(
        id, unit_time, total_time, counter, total_documents, time_string )
    __log(record)
