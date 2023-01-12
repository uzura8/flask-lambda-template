import os
from app.aws_s3_handler import AwsS3Handler
from app.models.dynamodb import Service
from app.common.media import get_mimetype_by_ext, get_exts_by_mimetypes
from app.common.image import Image


class MediaImageModifier:
    media_image_maker = None
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
        if 'debug_log_enabled' in options:
            self.debug_log_enabled = options.get('debug_log_enabled')

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
        return f'{self.bucket_dir_path}/{size}.{self.ext}'


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
