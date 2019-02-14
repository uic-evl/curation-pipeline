from requests import post
from os import listdir, remove
from os.path import join
from urllib import urlretrieve
from sys import exc_info
from zipfile import ZipFile

FIGSPLIT_LOG_NAME = 'FigSplitLog.txt'


class FigSplitWrapper:
    def __init__(self, _service_url):
        self.figsplit_url = _service_url

    def split(self, _folder_path):
        log_path = join(_folder_path, FIGSPLIT_LOG_NAME)
        logfile = open(log_path, 'w')

        figures = listdir(_folder_path)
        total_figures = 0
        successful_splits = 0

        for figure in figures:
            if figure.endswith((".jpg", ".png", ".jpeg", "bmp", "tif", ".tif")):
                total_figures += 1
                try:
                    r = post("%s/modified_uploader" % self.figsplit_url, files={
                        'file': open(join(_folder_path, figure), 'rb')
                    })
                    if r.status_code == 200:
                        self.__download_splitted_content(_folder_path, r, figure)
                        successful_splits += 1
                    else:
                        print r.status_code
                    # else do what?
                except Exception as e:
                    print 'Unexpected error: %s' % exc_info()[0]
                    logfile.write("%s: problem occurred\n%s" % (figure, e))

        logfile.close()
        return total_figures, successful_splits

    def __download_splitted_content(self, _folder_path, _response, _figure_name):
        html = _response.text.split('\n')
        for line in html:
            if 'download' in line and self.figsplit_url in line:
                link_of_zip = line.split('href="')[1].split('" download')[0]
                zip_name = '%s.zip' % _figure_name
                zip_path = join(_folder_path, zip_name)
                urlretrieve(link_of_zip, zip_path)
                FigSplitWrapper.__unpackage_zip(_folder_path, zip_name)
                remove(zip_path)

    @staticmethod
    def __unpackage_zip(_folder_path, zip_file):
        path_to_zip = join(_folder_path, zip_file)
        # zip files have this format: *.jpg.zip
        zip_name = zip_file[:-8]

        zip_ref = ZipFile(path_to_zip, 'r')
        zip_ref.extractall(join(_folder_path, zip_name))
        zip_ref.close()