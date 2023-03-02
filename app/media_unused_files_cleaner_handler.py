import os
import sys
from app.media_unused_files_cleaner import MediaUnusedFilesCleaner
from app.common.log import output_log

MEDIA_S3_BUCKET_NAME = os.environ.get('MEDIA_S3_BUCKET_NAME')
RESERVED_FILE_EXPIRATION_HOURS = \
        int(os.environ.get('MEDIA_UNUSED_FILES_CLEANER_RESERVED_FILE_EXPIRATION_HOURS', 12)) # Hours
DEBUG_LOG_ENABLED = os.environ.get('DEBUG_LOG_ENABLED') == 'true'


def handler(event=None, context=None):
    output_log('START: media_unused_files_cleaner.handler')
    output_log(['media_unused_files_cleaner.handler:event', event])

    if not MEDIA_S3_BUCKET_NAME:
        raise Exception('MEDIA_S3_BUCKET_NAME is not defined')

    try:
        options = {'debug_log_enabled': DEBUG_LOG_ENABLED}
        mufc = MediaUnusedFilesCleaner(MEDIA_S3_BUCKET_NAME,
                                       RESERVED_FILE_EXPIRATION_HOURS, None, options)
        mufc.main()
        output_log('END: media_unused_files_cleaner.handler: Success')
        return 'Success'

    except Exception as e:
        tb = sys.exc_info()[2]
        msg = e.with_traceback(tb)
        output_log(msg, 'error')
        return 'END: media_unused_files_cleaner.handler: Error'
