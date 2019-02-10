import json
from ntpath import basename
from os.path import join
from os import listdir
from requests import patch


class Task:
  def __init__(self, _insert_document_uri):
    self.insert_document_uri = _insert_document_uri

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
        with open(join(figsplit_output_path, '%s.txt' % figure[:-4]), 'r') as caption_file:
          caption = caption_file.read().decode('utf16')

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
    headers = {
      'Content-Type': 'application/json'
    }

    print self.insert_document_uri
    response = patch(self.insert_document_uri, data=data, headers=headers)

    if response.status_code == 200:
      return True
    return False


