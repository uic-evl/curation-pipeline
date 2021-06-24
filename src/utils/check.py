import os


def check_structure(f, base_path):
    content = os.listdir(os.path.join(base_path, f))
    pdfs = [x for x in content if '.pdf' in x.lower()]

    error = None
    if len(pdfs) == 0:
        error = "no main pdf"
    elif len(pdfs) > 1:
        error = "suppementary files not organized"
    if error:
        return False, error

    pdfigcapx_folder = os.path.join(base_path, f, pdfs[0][:-4])
    if not os.path.exists(pdfigcapx_folder):
        error = "pdfigcapx not executed"
    if error:
        return False, error

    content_figcapx = os.listdir(pdfigcapx_folder)
    if len(content_figcapx) == 0:
        return False, "no content extracted"
    if len(content_figcapx) == 1:
        # if there is one file, should be the json output
        if not (content_figcapx[0] == "{0}.json".format(pdfs[0][:-4])):
            return False, "missing json output"

    images = [x for x in content_figcapx if '.jpg' in x]
    count_images = len(images)
    count_folders = 0

    for image in images:
        fig_image_folder = os.path.join(pdfigcapx_folder, image[:-4])
        if os.path.exists(fig_image_folder):
            count_folders += 1
    if count_folders < count_images:
        return False, "figsplit incomplete"

    return True, None
