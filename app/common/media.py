import os

media_types = [
    {'mimetype':'image/jpeg', 'extensions':['jpg', 'jpeg']},
    {'mimetype':'image/png', 'extensions':['png']},
    {'mimetype':'image/gif', 'extensions':['gif']},
    {'mimetype':'application/pdf', 'extensions':['pdf']},
    {'mimetype':'application/msword', 'extensions':['doc']},
    {'mimetype':'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'extensions':['docx']},
    {'mimetype':'application/vnd.ms-powerpoint', 'extensions':['ppt']},
    {'mimetype':'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'extensions':['pptx']},
    {'mimetype':'application/vnd.ms-excel', 'extensions':['xls']},
    {'mimetype':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'extensions':['xlsx']},
    {'mimetype':'application/zip', 'extensions':['zip']},
    {'mimetype':'text/plain', 'extensions':['txt']},
    {'mimetype':'text/csv', 'extensions':['csv']},
]


def get_ext_by_mimetype(memetype):
    res = next((item for item in media_types if item['mimetype'] == memetype), False)
    if not res:
        return None

    return res['extensions'][0]


def get_mimetype_by_ext(ext):
    res = next((item for item in media_types if ext in item['extensions']), False)
    if not res:
        return None

    return res['mimetype']


def get_ext_by_path(filepath):
    dirname, basename = os.path.split(filepath)
    basename_without_ext, ext = basename.split('.', 1)
    return ext


def get_exts_by_mimetypes(mimetypes):
    exts = [ mt.split('/')[1] for mt in mimetypes ]
    if 'jpeg' in exts:
        exts.append('jpg')
    return exts
