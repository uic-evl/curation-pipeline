import argparse
import json
import os
from Pipeline import Pipeline
from datetime import datetime


def main():
    # read args from config_file or STDIN
    cli_parser = argparse.ArgumentParser(description='Pipeline')
    cli_parser.add_argument('-c', '--config_file', dest='config_file',
                            type=str, default=None, help='config file')
    cli_parser.add_argument('-chrome', '--chromedriver_path',
                            type=str, default=None, help='Chromedriver path')
    cli_parser.add_argument('-figsplit', '--figsplit_url',
                            type=str, default=None, help='Figsplit url')
    cli_parser.add_argument('-insert', '--insert_document_service_uri',
                            type=str, default=None, help='Insert service endpoint')
    cli_parser.add_argument('-send', '--send_task_service_uri',
                            type=str, default=None, help='Send task endpoint')

    cli_parser.add_argument('--organization', type=str, help='Organization')
    cli_parser.add_argument('--groupname', type=str, help='Group name')
    cli_parser.add_argument('--type', type=str, default='extract')
    cli_parser.add_argument('-log', '--logfilename',
                            type=str, default='PipelineLog.txt')

    cli_parser.add_argument('--input_path', type=str, default='',
                            help='Folder containing PDFs', required=True)
    cli_parser.add_argument('--output_path', type=str, default='',
                            help='Location of output files', required=True)
    cli_parser.add_argument(
        '--max_docs', type=int, default=100, help='Max number of documents to process')

    args, unknown = cli_parser.parse_known_args()
    parser = argparse.ArgumentParser(parents=[cli_parser], add_help=False)

    if args.config_file is not None:
        if args.config_file.endswith('.json'):
            config = json.load(open(args.config_file))
            parser.set_defaults(**config)
            [
                parser.add_argument(arg)
                for arg in [arg for arg in unknown if arg.startswith('--')]
                if arg.split('--')[-1] in config
            ]
        else:
            print("Configuration file should be a JSON file")
            return

    args = parser.parse_args()
    # when using a config file, check for organization and groupname
    if args.config_file is not None and (args.organization is None or args.groupname is None):
        parser.error(
            'with -c, *both* -groupname *and* -organization are required')
    # the following are always mandatory at least for linux systems
    if args.chromedriver_path is None or \
            args.figsplit_url is None or \
            args.insert_document_service_uri is None or \
            args.send_task_service_uri is None:
        parser.error(
            'please specify chromedriver, figsplit_url, insert_doc_service and send_task_service')

    # start pipeline
    if not os.path.exists(args.output_path):
        try:
            os.mkdir(args.output_path)
        except Exception as e:
            print("Could not create the output folder path")
            print(e)
            return

    number_docs_processed = 0
    config_settings = vars(args)
    pipeline = Pipeline(config_settings)
    input_documents = os.listdir(args.input_path)

    log_file_path = os.path.join(
        args.output_path, config_settings['logfilename'])
    with open(log_file_path, 'a+') as out:
        out.write('Batch execution:%s ---------------------\n' %
                  (datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        out.write('%d documents found in input folder:\n' %
                  len(input_documents))

    for input_doc in input_documents:
        if number_docs_processed < args.max_docs:
            input_document_path = os.path.join(args.input_path, input_doc)
            if pipeline.process_file(input_document_path, args.output_path):
                number_docs_processed += 1
        else:
            with open(log_file_path, 'a+') as out:
                out.write('Finished execution:%s ---------------------\n' %
                          (datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                out.write('%d processed\n\n' % len(args.max_docs))
            print("Reached maximum number of documents to process. Stopping execution")
            return


if __name__ == "__main__":
    main()
