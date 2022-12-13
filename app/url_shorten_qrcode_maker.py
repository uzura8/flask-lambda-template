import os
import sys
from io import BytesIO
import qrcode
from app.aws_s3_handler import AwsS3Handler
from app.common.log import output_log
from app.models.dynamodb import ShortenUrl

MEDIA_S3_BUCKET_NAME = os.environ.get('MEDIA_S3_BUCKET_NAME')
URL_SHORTEN_BASE_URL = os.environ.get('URL_SHORTEN_BASE_URL')
DEBUG_LOG_ENABLED = os.environ.get('DEBUG_LOG_ENABLED') == 'true'


class UrlShortenQrcodeMaker:
    s3handler = None
    bucket_dir_path = ''
    debug_log_enabled = False
    url_shorten_base_url = ''


    def __init__(self):
        self.debug_log_enabled = DEBUG_LOG_ENABLED
        self.url_shorten_base_url = URL_SHORTEN_BASE_URL
        self.s3handler = AwsS3Handler(MEDIA_S3_BUCKET_NAME)


    def __del__(self):
        pass


    def create_qrcode(self, url_id):
        item = ShortenUrl.get_one_by_pkey('urlId', url_id)
        if not item:
            raise InvalidValueError('urlId does not exist')

        shorten_url = self.url_shorten_base_url + url_id
        upload_key = 'shorten-url/qrcodes/%s.png' % url_id

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(shorten_url)
        qr.make()
        img = qr.make_image()

        buffer = BytesIO()
        img.save(buffer, 'PNG')
        buffer.seek(0)

        self.s3handler.upload(buffer, upload_key, 'image/png')
        output_log(['def url_shorten_qrcode_maker.create_qrcode', 'qrcode created', upload_key])


class InvalidValueError(Exception):
    pass


def handler(event=None, context=None):
    output_log('START: url_shorten_qrcode_maker.handler')
    output_log(['url_shorten_qrcode_maker.handler:event', event])

    qcm = UrlShortenQrcodeMaker()
    if event and 'Records' in event:
        for r in event['Records']:
            if r['eventName'] != 'INSERT':
                output_log(['def url_shorten_qrcode_maker.handler', 'Skip event for not INSERT'])
                continue

            err_cnt = 0
            try:
                url_id = r['dynamodb']['Keys']['urlId']['S']
                qcm.create_qrcode(url_id)

            except Exception as e:
                tb = sys.exc_info()[2]
                msg = e.with_traceback(tb)
                output_log(msg, 'error')
                err_cnt += 1

        return 'Success' if not err_cnt else 'END: url_shorten_qrcode_maker.handler: Error'
