import os

media_types = [
    {'mimetype':'image/jpeg', 'extensions':['jpg', 'jpeg']},
    {'mimetype':'image/png', 'extensions':['png']},
    {'mimetype':'image/gif', 'extensions':['gif']},
    {'mimetype':'application/pdf', 'extensions':['pdf']},
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
