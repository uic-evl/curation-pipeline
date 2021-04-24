import multiprocessing 
import time 
import subprocess
import sys

MAX_CPU = multiprocessing.cpu_count()

class Process(multiprocessing.Process): 
    def __init__(self, id): 
        super(Process, self).__init__() 
        self.id = id
                 
    def run(self): 
        print("running sub process: " + str(self.id))
        subprocess.call("python3 img_cap_extract.py "+ str(self.id), shell=True)
  
if __name__ == '__main__': 

    if len(sys.argv) < 2:
        processor_number = 1
    else:
        processor_number = int(sys.argv[1])
        if (processor_number >= MAX_CPU):
            print("Cannot reach the max of CPU: " + str(MAX_CPU))
            sys.exit()

    for i in range(0, processor_number):
        p = Process(i) 
        p.start()
        