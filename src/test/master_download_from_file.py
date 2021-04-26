import multiprocessing 
import time 
import subprocess
import sys
import math

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
        cmd = "python3 download_from_file.py {} {} {} ".format(str(self.file_path), str(self.page_size), str(self.id)) 
        subprocess.call(cmd, shell=True)
  
if __name__ == '__main__': 

    #run the file with paramter :"file_path" "number of processors"

    file_path = sys.argv[1]
    #todo validate is not a dir
    num_processors = int(sys.argv[2])
    #todo validate is not a number or not present
    
    import csv
    csvfile = open(file_path)
    reader = csv.reader(csvfile)
    total_rows= len(list(reader))
    print("Total rows {}".format(total_rows))
    print("Num Processors: {}".format(num_processors))
    page_size = math.ceil(total_rows / num_processors)
    print("Page size: {}".format(page_size))

    for i in range(1, num_processors+1):
        p = Process(i, page_size, file_path) 
        p.start()
   