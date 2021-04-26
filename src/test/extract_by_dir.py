import sys
import os
from os.path import join, abspath, exists
from os import mkdir, listdir
import subprocess
import time
from pathlib import Path

#parameter input_path
input_path = '/mnt/wormbase/positives' if len(sys.argv) < 2 else str(sys.argv[1])
output_path = '/mnt/wormbase/output' if len(sys.argv) < 3 else str(sys.argv[2])
log_path = '/mnt/wormbase/log' if len(sys.argv) < 4 else str(sys.argv[3])

#validate directories
if not exists(input_path):
    print("input path does not exist: " + str(input_path))
    sys.exit()
if not exists(output_path):
    print("output path does not exist: " + str(output_path))
    sys.exit()
if not exists(log_path):
    print("log path does not exist: " + str(log_path))
    sys.exit()

chrome_driver_path = join('/usr/bin/chromedriver')
xpdf_pdftohtml_path = "/usr/local/bin/pdftohtml"

current_dir = os.getcwd()
source_dir = abspath(join(current_dir, '..'))
sys.path.append(source_dir)

from PDFigCapX import PDFigCapX
p = PDFigCapX(_chrome_drive_path=chrome_driver_path,
              _xpdf_pdftohtml_path=xpdf_pdftohtml_path)

total_files, total_pdf, total_successes = p.extract(input_path, output_path, log_path, True)

print(str(input_path.split('/')[-1]) + " Completed.")