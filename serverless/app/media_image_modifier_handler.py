import os
import sys
import urllib.parse
from app.media_image_maker import MediaImageMaker
from app.models.dynamodb import File, ServiceConfig
from app.common.site import media_accept_mimetypes, get_service_config_value
from app.common.media import get_ext_by_mimetype
from app.common.log import output_log

DEBUG_LOG_ENABLED = os.environ.get('DEBUG_LOG_ENABLED') == 'true'

class MediaImageModifier:

    service_id = ''
    bucket_name = ''
    files = []
    last_evaluated_key = None
    media_image_maker = None


    def __init__(self, service_id, bucket_name, media_image_maker_opts):
        self.service_id = service_id
        self.bucket_name = bucket_name
        self.media_image_maker = MediaImageMaker(service_id, media_image_maker_opts)


    def __del__(self):
        pass


    def main(self):
        done = False
        start_key = None
        opts = {}
        while not done:
            if start_key:
                opts['ExclusiveStartKey'] = start_key
            res = File.scan(opts, True)
            start_key = res.get('LastEvaluatedKey', None)
            self.files = res.get('Items', [])
            self.create_images()
            done = start_key is None


    def create_images(self):
        if not self.files:
            return

        for file in self.files:
            file_id = file['fileId']
            ext = get_ext_by_mimetype(file['mimeType'])
            bucket_path = f'{self.service_id}/images/{file_id}/raw.{ext}'
            self.media_image_maker.main(self.bucket_name, bucket_path)


# Event Json Sample
#{
#    "bucketName": "media.example.com",
#    "serviceId": "hoge",
#}

def handler(event=None, context=None):
    output_log('START: media_image_modifier.handler')
    output_log(['media_image_modifier.handler:event', event])

    bucket_name = event['bucketName']
    service_id = event['serviceId']

    service_configs = ServiceConfig.get_all_by_service(service_id, True, True, True)
    accept_mimetypes = media_accept_mimetypes('image', service_configs)
    image_sizes = get_service_config_value('mediaUploadImageSizes', service_configs)

    try:
        image_maker_opts = {
            'accept_mimetypes': accept_mimetypes,
            'image_sizes': image_sizes,
            'debug_log_enabled': DEBUG_LOG_ENABLED,
        }
        mim = MediaImageModifier(service_id, bucket_name, image_maker_opts)
        mim.main()
        output_log('END: media_image_modifier.handler: Success')
        return 'Success'

    except Exception as e:
        tb = sys.exc_info()[2]
        msg = e.with_traceback(tb)
        #mim.send_result_mail('error', {'error_msg': msg})
        output_log(msg, 'error')
        return 'END: media_image_modifier.handler: Error'
