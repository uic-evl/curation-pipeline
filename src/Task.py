from ntpath import basename
from os.path import join
from os import listdir
from requests import post


class Task:
  def __init__(self, _insert_document_uri):
    self.insert_document_uri = _insert_document_uri

  def create_document(self, _folder_path, _entity_id=None):
    pubmed_id = basename(_folder_path)
    filename = '%s.pdf' % pubmed_id
    uri = join(_folder_path, filename)
    entity_id = _entity_id

    figures = []
    elems = listdir(_folder_path)
    for elem in elems:
      if elem.startswith('p'):  # it is a folder processed by the pipeline
        p_elems = listdir(join(_folder_path, elem))
        # first get the 'compound figures'
        for p_elem in p_elems:
          if p_elem.endswith('.jpg'):
            figure_filename = p_elem
            figure_uri = join(_folder_path, elem, figure_filename)
            subfigures_folder = join(_folder_path, elem, figure_filename[-4])
            subfigures = []
            for subfigure in listdir(subfigures_folder):
              if subfigure.endswith('.jpg'):
                subfigures.append({
                  "name": subfigure[:-4],
                  "uri": join(subfigures_folder, subfigure)
                })
            figures.append({
              "name": figure_filename[:-4],
              "uri": join(_folder_path, elem, figure_filename),
              "subfigures": subfigures
            })
    return {
      "name": filename,
      "pubmed_id": pubmed_id,
      "uri": uri,
      "entity_id": entity_id,
      "figures": figures
    }

  def insert_document(self, document):
    data = { "document": document}
    response = post(self.insert_document_uri, data=data)
    if response.status_code == 200:
      return True
    return False


