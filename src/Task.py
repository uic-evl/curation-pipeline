import json
from ntpath import basename
from os.path import join, exists
from os import listdir
from urllib.requests import patch


class Task:
    def __init__(self, _insert_document_uri, _send_task_uri):
        self.insert_document_uri = _insert_document_uri
        self.send_task_uri = _send_task_uri

    def create_document(self, _folder_path, _entity_id=None):
        pubmed_id = basename(_folder_path)[1:]
        filename = '%s.pdf' % pubmed_id
        relative_uri = join("/", basename(_folder_path))
        entity_id = _entity_id

        figures = []
        figsplit_output_path = join(_folder_path, pubmed_id)
        elems = listdir(figsplit_output_path)

        # first get the 'compound figures'
        for figure in elems:
            if figure.endswith('.jpg'):
                subfigures_folder = join(figsplit_output_path, figure[:-4])
                caption_file_path = join(
                    figsplit_output_path, '%s.txt' % figure[:-4])
                if exists(caption_file_path):
                    with open(join(figsplit_output_path, '%s.txt' % figure[:-4]), 'r') as caption_file:
                        caption = caption_file.read()
                else:
                    caption = 'no caption extracted for this image'

                subfigures = []
                for subfigure in listdir(subfigures_folder):
                    if subfigure.endswith('.jpg'):
                        subfigures.append({
                            "name": subfigure[:-4],
                            "uri": join(relative_uri, pubmed_id, basename(subfigures_folder), subfigure)
                        })
                figures.append({
                    "name": figure[:-4],
                    "uri": join(relative_uri, pubmed_id, figure),
                    "subfigures": subfigures,
                    "caption": caption
                })
        return {
            "name": filename,
            "pubmedId": pubmed_id,
            "uri": join(relative_uri, filename),
            "entityId": entity_id,
            "figures": figures
        }

    def insert_document(self, document):
        data = json.dumps({"document": document})
        # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        headers = {'Content-Type': 'application/json'}

        response = patch(self.insert_document_uri, data=data, headers=headers)

        if response.status_code == 200:
            return response.json(), None
        return None, str(data) + '\n\n' + str(response)

    def send_task(self, doc_id, doc_name, organization, group_name):
        data = json.dumps({
            "documentId": doc_id,
            "documentName": doc_name,
            "organization": organization,
            "groupname": group_name
        })

        headers = {'Content-Type': 'application/json'}
        response = patch(self.send_task_uri, data=data, headers=headers)

        if response.status_code == 200:
            return response.json()
        return None
