import requests
import xmltodict
import json
import os
from os.path import join, isdir
from contextlib import closing
import urllib.request as request
import shutil
import time

PMC_URL = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={0}"
CMD_EXTRACT_PDF = 'for f in $(tar -tzf {0} | grep -E ".pdf$"); do tar -C {1} -zxf {0} "$f" ; done'
ERROR_FILE = "download_error.log"
TRACKER_FILE = "download_track.csv"

class DownloadPaper():
    def __init__(self, _output_path, _log_path):
        self.log_file = None
        self.output_path = _output_path        
        self.error_file = join(_log_path, ERROR_FILE)
        self.track_file = join(_log_path, TRACKER_FILE)

    def get_targz_location(self, pmcid):
        uri = PMC_URL.format(pmcid)
        response = requests.request('get', uri)
        
        if response.ok:
            res_od = xmltodict.parse(response.content)
            res_str = json.dumps(res_od)
            res_json = json.loads(res_str)
            
            try:
                if 'error' in res_json['OA']:
                    msg = str(res_json['OA']['error']['#text'])
                    self.__logError(pmcid, msg)
                    self.__track(pmcid, 'E', msg)
                    return (None, msg)
                
                links = res_json['OA']['records']['record']['link']
                if isinstance(links, dict): # when it's one single element
                    links = [links]         # make it a list for later processing
                result = list(filter(lambda x: x['@format'] == 'tgz', links))
                if len(result) > 0:
                    return (result[0]['@href'], None)
                else:
                    msg = 'No PDF available'
                    self.__logError(pmcid, msg)
                    self.__track(pmcid, 'E', msg)
                    return (None, msg)
            except Exception as e:
                msg = 'Exception {0}'.format(str(e))
                self.__logError(pmcid, msg)
                self.__track(pmcid, 'E', msg)
                return (None, msg)

        msg = 'Response error {0}'.format(response.status_code)
        self.__logError(pmcid, msg)
        self.__track(pmcid, 'E', msg)
        return (None, msg)

    def download_and_extract(self, url, _id):
        try:
            filename = url.split('/')[-1]
            filepath = os.path.join( self.output_path, filename)
            
            with closing(request.urlopen(url)) as r:
                with open(filepath, 'wb') as f:
                    shutil.copyfileobj(r, f)
            
            os.system(CMD_EXTRACT_PDF.format(filepath,  self.output_path))
            os.remove(filepath)
            #If dir was created -> there was pdf; otherwise no pdf was there.
            if isdir(join( self.output_path, _id)):
                self.__track(str(_id), 'S', 'Ok')
            else:
                self.__track(str(_id), 'E', 'No PDF in the compressed file')
        except Exception as e:
            self.__track(str(_id), 'E', 'Exception {0}'.format(str(e)))
            self.__logError(str(_id),'Exception {0}'.format(str(e)))

    def download_batch_ids(self, ids , output_dir):
        for id in ids:
            ftp_url, error = self.get_targz_location(id)
            if not error:
                start = time.perf_counter()
                print("Downloading: " + id)
                self.download_and_extract(ftp_url, output_dir)
                end = time.perf_counter()
                taken_time = end - start
                taken_time = round(taken_time, 3)
                print("\ttime: " + str(taken_time))
                
            else:
                print('{0}: {1}'.format(id, ftp_url if not error else error))

    def __track(self, _id, _status, _message):
        record = str(_id) + "|" + str(_status) + "|" + str(_message)
        os.system("echo '"+record+"' >> " + self.track_file)

    def __logError(self, _id, _error):
        time_string = time.strftime("%m/%d/%Y@%H:%M:%S", time.localtime())
        record = time_string+"|"+str(_id) + "|" + str(_error)
        print("\t"+record)
        os.system("echo '"+record+"' >> " + self.error_file)