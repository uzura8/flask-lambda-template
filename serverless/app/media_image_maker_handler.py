import os
import sys
import urllib.parse
from app.media_image_maker import MediaImageMaker
from app.models.dynamodb import ServiceConfig
from app.common.site import media_accept_mimetypes, get_service_config_value
from app.common.media import get_exts_by_mimetypes
from app.common.log import output_log

FILE_SIZE_LIMIT = int(os.environ.get('MEDIA_IMAGE_MAKER_FILE_SIZE_LIMIT', 1)) # MB
DEBUG_LOG_ENABLED = os.environ.get('DEBUG_LOG_ENABLED') == 'true'


def handler(event=None, context=None):
    output_log('START: media_image_maker.handler')
    output_log(['media_image_maker.handler:event', event])

    output_log((222200000, event))
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
        raise Exception(f'File size {file_size} is over limit')

    try:
        options = {
            'accept_mimetypes': accept_mimetypes,
            'image_sizes': image_sizes,
            'debug_log_enabled': DEBUG_LOG_ENABLED,
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
