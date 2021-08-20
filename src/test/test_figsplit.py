import sys
import logging
from os import getcwd, listdir
from os.path import abspath, join
from core.FigSplitWrapper import FigSplitWrapper

current_folder = getcwd()
source_folder = abspath(join(current_folder, '..'))
sys.path.append(source_folder)

base_path = '/mnt/files/output/uic'
reprocess_files = '/mnt/files/reprocess_figsplit.txt'
success_files = '/mnt/files/success_figsplit.txt'
error_files = '/mnt/files/error_figsplit.txt'


def read_ids(filename):
    try:
        with open(filename, 'r') as file:
            ids = file.read().splitlines()
    except FileNotFoundError:
        print(f'{filename} does not exist')
        ids = []
    return ids


reprocess_ids = read_ids(reprocess_files)
success_ids = read_ids(success_files)
error_ids = read_ids(error_files)

FIGSPLIT_URL = 'https://www.eecis.udel.edu/~compbio/FigSplit'
fsw = FigSplitWrapper(FIGSPLIT_URL)

ids = [x for x in reprocess_ids if x not in success_ids and x not in error_ids]
print("processing {0} files".format(len(ids)))

for _id in ids:
    input_folder_path = join(base_path, _id)
    pdf = [x for x in listdir(input_folder_path) if '.pdf' in x][0]
    input_folder_path = join(input_folder_path, pdf[:-4])

    total_figures, total_figures_splitted = fsw.split(input_folder_path)

    sucess = total_figures == total_figures_splitted
    output_filepath = success_files if sucess else error_files
    with open(output_filepath, 'a') as file:
        file.write("{0}\n".format(_id))
    print(_id, sucess, total_figures, total_figures_splitted)
