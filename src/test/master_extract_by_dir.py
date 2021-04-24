import multiprocessing 
import time 
import subprocess
import sys

class Process(multiprocessing.Process): 
    def __init__(self, id): 
        super(Process, self).__init__() 
        self.id = id
                 
    def run(self): 
        print("running sub process: " + str(self.id))
        #cmd = "python3 extract_by_dir.py /workspace/allen/Allen-Collection-Curation/input/"+str(self.id)+" /workspace/allen/Allen-Collection-Curation/output/output_pos_neg /workspace/allen/Allen-Collection-Curation/log/log_pos_neg > /workspace/allen/Allen-Collection-Curation/log/log_pos_neg/extractByDir_"+str(self.id)+".log"
        cmd = "python3 extract_by_dir.py /mnt/wormbase/"+str(self.id)+" /mnt/wormbase_output /mnt/wormbase_log > /mnt/wormbase_log/mainLog_"+str(self.id)+".log"
        subprocess.call(cmd, shell=True)

if __name__ == '__main__': 

    p = Process('positives') 
    p.start()

    p = Process('negatives') 
    p.start()
        