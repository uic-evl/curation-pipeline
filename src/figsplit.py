from os import listdir
from os.path import join, exists
from core.FigSplitWrapper import FigSplitWrapper
import concurrent.futures
import logging
import argparse

FIGSPLIT_URL = 'https://www.eecis.udel.edu/~compbio/FigSplit'
# base_path = '/mnt/files/output/uic'
# reprocess_files = '/mnt/files/reprocess_figsplit.txt'
# success_files = '/mnt/files/success_figsplit.txt'
# error_files = '/mnt/files/error_figsplit.txt'


def setup_logger(logger_filepath):
    logger = logging.getLogger(__name___)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")

    file_handler = logging.FileHandler(logger_filepath)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


def read_ids(filename):
    try:
        with open(filename, 'r') as file:
            ids = file.read().splitlines()
    except FileNotFoundError:
        print(f"{filename} file not yet created")
        ids = []
    return ids


def process_folder(_id, input_path, success_filepath, error_filepath,
                   logger_filepath):
    logger = logging.getLogger(logger_filepath)

    input_folder_path = join(input_path, _id)
    pdf = [x for x in listdir(input_folder_path) if '.pdf' in x][0]
    input_folder_path = join(input_folder_path, pdf[:-4])

    fsw = FigSplitWrapper(FIGSPLIT_URL)
    total_figures, total_figures_splitted = fsw.split(input_folder_path)

    sucess = total_figures == total_figures_splitted
    output_filepath = success_filepath if sucess else error_filepath
    with open(output_filepath, 'a') as file:
        file.write("{0}\n".format(_id))
    logger.info(_id, sucess, total_figures, total_figures_splitted)


def main():
    parser = argparse.ArgumentParser(description="batch proc figsplit")
    parser.add_argument('--input', type=str,
                        help="folder containing folders to process")
    parser.add_argument('--base_path', type=str,
                        help="folder path for output ids")

    args = parser.parse_args()

    if not exists(args.input) or not exists(args.base_path):
        print("File paths in arguments do not exists")
        return

    reprocess_filepath = join(args.base_path, "reprocess_figsplit.txt")
    success_filepath = join(args.base_path, "success_figsplit.txt")
    error_filepath = join(args.base_path, "error_figsplit.txt")
    logger_filepath = join(args.base_path, "logger_batch_figsplit.log")

    logger = setup_logger(logger_filepath)
    reprocess_ids = read_ids(reprocess_filepath)
    if len(reprocess_ids == 0):
        logger.error("File with ids to process is empty")
        return
    success_ids = read_ids(success_filepath)

    ids = [x for x in reprocess_ids if x not in success_ids]
    logger.info(f'Started processing {len(ids)} files')

    try:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(process_folder, ids,
                         [args.input] * len(ids),
                         [success_filepath] * len(ids)
                         [error_filepath] * len(ids)
                         [args.logger] * len(ids))
    except Exception:
        logger.exception("exception caught while batch processing")
    finally:
        logger.info("finished batch processing")


if __name__ == "__main__":
    main()
