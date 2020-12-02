# Curation-Pipeline

Where we receive one or more PDFs, extract the figures and captions (`PDFigCapX`), split the figures into subfigures (`FigSplit`) and store the information in the curation database. While database stores the metadata, we store the PDF, figures, subfigures and extraction logs are stored in an user-determined output folder. For the curation front-end purposes, this locations should be the folder serving the static files.

## Dependencies

`PDFigCapX` uses Selenium, Xpdf command line tools, and ImageMagick to extract the document content. Therefore, the environment should have installed a chrome-driver, and Xpdf/bin64 and ImageMagick/convert.exe should be available on a given location (`DEPENDENCIES`).

To store the databse content and create a task on the curation system, we need to specify the endpoints for those services on the configuration file (config.json) or through command line arguments (see `main.py`).

We wrote the pipeline originally in Python 2.7 but then migrated most of the content to Python 3.X. However, `PDFigCapX` binaries (in the compiled folder) still use Python 2.7. We integrated these components using `execnet` but hopefully we will have a native Python 3.X soon. Finally, `PDFigCapX` relies on opencv 2.4.X which is no longer available as a PiPy package. We solved this problem by building opencv from source. For more details about all the dependencies setup, please refer to the Dockerfile for Ubuntu 18.04.

## Running from command line (legacy)

1. Place the PDFs documents on a folder.
2. Locate your output folder. **Limitation:** the pipeline skips a document if the output folder already contains a document with the same name.
3. Set up `config.json` with the location of binaries and endpoints. Also, indicate the `groupname` and `organization` to apply the round-robin strategy for task delegation.
4. Execute the following commands. **MAX_NUMBER_DOCS** indicates the maximum number of documents to process at this time; if you need to process all the documents, enter a big number.

```
Xvfb :99 & export DISPLAY=:99 # run chromedriver headless
python pipeline_runner.py /route/to/config.json /route/to/input/folder /route/to/output/folder MAX_NUMBER_DOCS
```
