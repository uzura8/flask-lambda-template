import json
import os
import sys
import urllib.parse
from app.aws_s3_handler import AwsS3Handler
from app.models.dynamodb import Service, ServiceConfig
from app.common.site import media_accept_mimetypes, get_service_config_value
from app.common.media import get_mimetype_by_ext
from app.common.image import Image
from app.common.log import output_log

FILE_SIZE_LIMIT = int(os.environ.get('MEDIA_IMAGE_MAKER_FILE_SIZE_LIMIT', 1)) # MB
DEBUG_LOG_ENABLED = os.environ.get('DEBUG_LOG_ENABLED') == 'true'


def get_exts_by_mimetypes(mimetypes):
    exts = [ mt.split('/')[1] for mt in mimetypes ]
    if 'jpeg' in exts:
        exts.append('jpg')
    return exts


class MediaImageMaker:
    s3handler = None
    service_id = ''
    bucket_dir_path = ''

    accept_mimetypes = []
    accept_exts = []
    image_sizes = []

    image_raw = None
    ext = ''
    mimetype = ''

    debug_log_enabled = False
    #notice_emails = None
    #ses_region = ''


    def __init__(self, service_id, options):
        self.debug_log_enabled = DEBUG_LOG_ENABLED
        #self.ses_region = SES_REGION

        if not Service.check_exists(service_id):
            raise InvalidValueError('ServiceId does not exist')

        self.service_id = service_id
        self.accept_mimetypes = options.get('accept_mimetypes')
        self.accept_exts = get_exts_by_mimetypes(self.accept_mimetypes)
        self.image_sizes = options.get('image_sizes')


    def __del__(self):
        pass


    def main(self, bucket_name, obj_key):
        self.set_props_by_obj_key(obj_key)
        self.s3handler = AwsS3Handler(bucket_name)
        file_bin = self.s3handler.get_data(obj_key)
        self.image_raw = Image(file_bin)
        self.make_thumbnails()


    def make_thumbnails(self):
        for size_str in self.image_sizes:
            self.make_thumbnail(size_str)


    def make_thumbnail(self, size_str):
        if not self.image_raw:
            return

        width, height, resize_type = self.conv_size_str_to_list(size_str)
        upload_key = self.get_obj_key_by_size(size_str)
        resized_blob = self.image_raw.resize(width, height, resize_type)
        self.s3handler.upload(resized_blob, upload_key, self.mimetype)


    def set_props_by_obj_key(self, obj_key):
        self.bucket_dir_path = '/'.join(obj_key.strip('/').split('/')[:-1])
        self.ext = os.path.splitext(obj_key)[1][1:]
        self.mimetype = get_mimetype_by_ext(self.ext)


    def get_obj_key_by_size(self, size='raw'):
        return '%s/%s.%s' % (self.bucket_dir_path, size, self.ext)


    @staticmethod
    def conv_size_str_to_list(size_str):
        items = size_str.split('x')
        if len(items) < 3:
            resize_type = 'relative'
        elif items[2] == 'c':
            resize_type = 'relative_crop'
        elif items[2] == 's':
            resize_type = 'square_crop'

        return (int(items[0]), int(items[1]), resize_type)


class InvalidValueError(Exception):
    pass


def handler(event=None, context=None):
    output_log('START: media_image_maker.handler')
    output_log(['media_image_maker.handler:event', event])

    s3_event = event['Records'][0]['s3']
    bucket_name = s3_event['bucket']['name']
    bucket_path = urllib.parse.unquote_plus(s3_event['object']['key'], encoding='utf-8')
    file_size = s3_event['object']['size']

    path_items = bucket_path.strip('/').split('/')
    if len(path_items) < 4:
        return 'Object key is out of target'

    file_type = path_items[1]
    if file_type != 'images':
        return "Object key dosen't include 'images'"

    file_item = path_items[-1].split('.')
    if len(file_item) < 2:
        return "Object key has no extension"

    file_name = file_item[0]
    if file_name != 'raw':
        return f'File name {file_name} is out of target'

    service_id = path_items[0]
    service_configs = ServiceConfig.get_all_by_service(service_id, True, True, True)
    accept_mimetypes = media_accept_mimetypes('image', service_configs)
    image_sizes = get_service_config_value('mediaUploadImageSizes', service_configs)
    allowed_exts = get_exts_by_mimetypes(accept_mimetypes)

    ext = file_item[-1]
    if ext not in allowed_exts:
        return f'File extension {ext} is out of target'

    file_size_limit = FILE_SIZE_LIMIT * 1024 * 1024
    if file_size > file_size_limit:
        raise Exception('File size %d is over limit' % file_size)

    try:
        options = {
            'accept_mimetypes': accept_mimetypes,
            'image_sizes': image_sizes,
        }
        mim = MediaImageMaker(service_id, options)
        mim.main(bucket_name, bucket_path)
        output_log('END: media_image_maker.handler: Success')
        return 'Success'

    except Exception as e:
        tb = sys.exc_info()[2]
        msg = e.with_traceback(tb)
        #mim.send_result_mail('error', {'error_msg': msg})
        output_log(msg, 'error')
        return 'END: media_image_maker.handler: Error'
