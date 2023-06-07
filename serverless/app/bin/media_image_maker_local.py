"""
This script is execute MediaImageMaker on local

positional arguments:
  service_id
  bucket_name
  file_id
  ext

You need set env variable "PRJ_PREFIX" like below

export PRJ_PREFIX=gpcms-dev
"""

import os
import sys
import argparse
from pprint import pprint

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

from app.media_image_maker import MediaImageMaker
from app.models.dynamodb import ServiceConfig
from app.common.site import media_accept_mimetypes, get_service_config_value
from app.common.media import get_exts_by_mimetypes
from app.common.log import output_log

DEBUG_LOG_ENABLED = os.environ.get('DEBUG_LOG_ENABLED') == 'true'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This script is execute MediaImageMaker on local')
    parser.add_argument('service_id')
    parser.add_argument('bucket_name')
    parser.add_argument('file_id')
    parser.add_argument('ext')
    args = parser.parse_args()

    service_id = args.service_id
    service_configs = ServiceConfig.get_all_by_service(service_id, True, True, True)
    accept_mimetypes = media_accept_mimetypes('image', service_configs)
    image_sizes = get_service_config_value('mediaUploadImageSizes', service_configs)
    allowed_exts = get_exts_by_mimetypes(accept_mimetypes)

    try:
        file_id = args.file_id
        ext = args.ext
        bucket_path = f'pal-gunma/images/{file_id}/raw.{ext}'
        options = {
            'accept_mimetypes': accept_mimetypes,
            'image_sizes': image_sizes,
            'debug_log_enabled': DEBUG_LOG_ENABLED,
        }
        #print((service_id, options, args.bucket_name, bucket_path)) # FOR DEBUG
        mim = MediaImageMaker(service_id, options)
        mim.main(args.bucket_name, bucket_path)
        output_log('END: media_image_maker.handler: Success')
        print('Success')

    except Exception as e:
        tb = sys.exc_info()[2]
        msg = e.with_traceback(tb)
        #mim.send_result_mail('error', {'error_msg': msg})
        output_log(msg, 'error')
        print('END: media_image_maker.handler: Error')
