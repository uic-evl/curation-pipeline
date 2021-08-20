from os.path import join, exists
from core.PDFigCapX import PDFigCapX
import concurrent.futures
import logging
import argparse

chrome_driver_path = join('/usr/bin/chromedriver')
xpdf_pdftohtml_path = "/usr/local/bin/pdftohtml"


def setup_logger(logger_filepath):
    logger = logging.getLogger()
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

    p = PDFigCapX(_chrome_drive_path=chrome_driver_path,
                  _xpdf_pdftohtml_path=xpdf_pdftohtml_path)

    pdfs_err_list, total_pdf, total_successes = p.extract(
        input_folder_path, input_folder_path)
    success = total_pdf == total_successes
    output_filepath = success_filepath if success else error_filepath
    with open(output_filepath, 'a') as file:
        file.write("{0}\n".format(_id))
    logger.info(f"{_id}\t {success}\t {total_pdf}\t {total_successes}")


def main():
    parser = argparse.ArgumentParser(description="batch pdfigcapx")
    parser.add_argument('--input', type=str,
                        help="folder containing folders to process")
    parser.add_argument('--base_path', type=str,
                        help="folder path for output ids")

    args = parser.parse_args()

    if not exists(args.input) or not exists(args.base_path):
        print("File paths in arguments do not exists")
        return

    reprocess_filepath = join(args.base_path, "reprocess_pdfigcapx.txt")
    success_filepath = join(args.base_path, "success_pdfigcapx.txt")
    error_filepath = join(args.base_path, "error_pdfigcapx.txt")
    logger_filepath = join(args.base_path, "logger_batch_pdfigcapx.log")

    logger = setup_logger(logger_filepath)
    reprocess_ids = read_ids(reprocess_filepath)
    if len(reprocess_ids) == 0:
        logger.error("File with ids to process is empty")
        return
    success_ids = read_ids(success_filepath)

    ids = [x for x in reprocess_ids if x not in success_ids]
    logger.info(f'Started processing {len(ids)} files')

    try:
        for _id in ids:
            process_folder(_id, args.input, success_filepath,
                           error_filepath, logger_filepath)
        # with concurrent.futures.ProcessPoolExecutor() as executor:
        #     executor.map(process_folder, ids,
        #                  [args.input] * len(ids),
        #                  [success_filepath] * len(ids),
        #                  [error_filepath] * len(ids),
        #                  [logger_filepath] * len(ids))
    except Exception:
        logger.exception("exception caught while batch processing")
    finally:
        logger.info("finished batch processing")


if __name__ == "__main__":
    main()
