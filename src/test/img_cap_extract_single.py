import sys
import os
from os.path import join, abspath, exists
from os import mkdir, listdir
import subprocess
import time
from pathlib import Path

#python3 img_cap_extract_single.py {path_pmci} {log_path} 
input_dir = sys.argv[1]
output_path = input_dir
log_path = sys.argv[2]

current_dir = os.getcwd()
source_dir = abspath(join(current_dir, '..'))
sys.path.append(source_dir)

chrome_driver_path = join('/usr/bin/chromedriver')
xpdf_pdftohtml_path = "/usr/local/bin/pdftohtml"

from PDFigCapX import PDFigCapX
p = PDFigCapX(_chrome_drive_path=chrome_driver_path,
_xpdf_pdftohtml_path=xpdf_pdftohtml_path)

start_time = time.perf_counter()

total_files, total_pdf, total_successes = p.extract(
    input_dir, output_path, log_path, False)

finish_time = time.perf_counter()
total_time = finish_time - start_time
total_time = round(total_time, 3)
time_string = time.strftime("%H:%M:%S %m/%d/%Y", time.localtime())
print("\tTime: {} | #files: {} | #Total pdfs: {} | at {}".format(
    total_time,  total_files, total_pdf, time_string ))
print("Completed.")