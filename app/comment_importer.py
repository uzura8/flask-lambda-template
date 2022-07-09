import csv
import io
import json
import os
import boto3
from app.common.list import find_dicts
from app.common.date import utc_iso, str2dt, date_to_zfill
from app.common.log import output_log
from app.models.dynamodb import Comment, CommentCount, Service, ModelInvalidParamsException

COMMENT_IMPORTER_COLUMN_CONVERSION_TABLE =\
    os.environ.get('COMMENT_IMPORTER_COLUMN_CONVERSION_TABLE', '')
COMMENT_IMPORTER_CONTENT_LIST = os.environ.get('COMMENT_IMPORTER_CONTENT_LIST', '')
COMMENT_IMPORTER_SIZE_LIMIT = int(os.environ.get('COMMENT_IMPORTER_SIZE_LIMIT', 1)) # MB
COMMENT_IMPORTER_ROWS_COUNT_LIMIT = int(os.environ.get('COMMENT_IMPORTER_ROWS_COUNT_LIMIT', 1000))
DEBUG_LOG_ENABLED = bool(os.environ.get('DEBUG_LOG_ENABLED', False))


class CommentImporter:
    s3 = None
    service_id = ''
    conv_table = None
    content_list = None
    file_size_limit = 0
    saved_comment_ids = []
    update_attrs = ['publishStatus', 'body', 'contentId', 'profiles']
    debug_log_enabled = False


    def __init__(self, service_id):
        self.debug_log_enabled = DEBUG_LOG_ENABLED

        if not Service.check_exists(service_id):
            raise InvalidValueError('ServiceId does not exist')

        self.service_id = service_id
        self.s3 = boto3.resource('s3')

        conv_table_dict = json.loads(COMMENT_IMPORTER_COLUMN_CONVERSION_TABLE)
        if self.service_id not in conv_table_dict:
            msg = 'Column conversion table is not defined for %s' % self.service_id
            raise InvalidValueError(msg)
        self.conv_table = conv_table_dict[self.service_id]

        content_list_dict = json.loads(COMMENT_IMPORTER_CONTENT_LIST)
        if self.service_id not in content_list_dict:
            msg = 'Content list is not defined for %s' % self.service_id
            raise InvalidValueError(msg)
        self.content_list = content_list_dict[self.service_id]

        self.file_size_limit = COMMENT_IMPORTER_SIZE_LIMIT * 1024 * 1024


    def __del__(self):
        pass


    def main(self, bucket_name, obj_key, file_size):
        self.check_file_size_limit(file_size)

        self.set_saved_comment_ids()
        s3obj = self.s3.Object(bucket_name, obj_key).get()
        stream = io.TextIOWrapper(io.BytesIO(s3obj['Body'].read()), encoding='sjis')
        for idx, row in enumerate(csv.DictReader(stream)):
            if idx >= COMMENT_IMPORTER_ROWS_COUNT_LIMIT:
                output_log('Stop import for over rows count limit: %s' \
                            % COMMENT_IMPORTER_ROWS_COUNT_LIMIT)
                break

            item = self.conv_to_save_item(row)
            self.save_comment(item)


    def conv_to_save_item(self, row):
        vals = {}
        profiles = {}
        none_conv_attrs = ['body', 'ua', 'ip', 'localId']
        for k, v in row.items():
            save_attr = self.conv_table.get(k)
            if not save_attr:
                continue

            if save_attr == 'createdAt':
                date_str = self.ajust_date_format(v)
                dt = str2dt(date_str)
                vals[save_attr] = utc_iso(False, True, dt)
            elif save_attr == 'unpublish':
                vals['publishStatus'] = 'unpublish' if v == '1' else 'publish'
            elif save_attr == 'contentLabel':
                vals['contentId'] = self.get_contentId_from_label(v)
            elif save_attr.startswith('profiles:'):
                attr = save_attr.split(':')[1]
                profiles[attr] = v
            elif save_attr in none_conv_attrs:
                vals[save_attr] = v

        content_id = vals.get('contentId')
        if not content_id:
            raise InvalidValueError('Failed to get contentId')

        local_id = vals.get('localId')
        if not local_id:
            raise InvalidValueError('Failed to get localId')

        vals['statusCreatedAt'] = '#'.join([vals['publishStatus'], vals['createdAt']])
        vals['profiles'] = profiles
        vals['serviceId'] = self.service_id
        vals['contentId'] = content_id
        vals['serviceIdContentId'] = '#'.join([self.service_id, content_id])
        vals['commentId'] = self.gen_comment_id(self.service_id, local_id)
        vals['localId'] = local_id
        return vals


    def save_comment(self, vals):
        comment_id = vals['commentId']
        if comment_id in self.saved_comment_ids:
            output_log({
                'func':'save_comment-0',
                'msg': 'update',
                'commentId': comment_id,
            })
            self.update_comment(vals)
        else:
            output_log({
                'func':'save_comment-1',
                'msg': 'create',
                'commentId': comment_id,
            })
            Comment.create(vals)


    def update_comment(self, vals):
        #content_id = vals['contentId']
        comment_id = vals['commentId']
        query_keys = {'p': {'key':'commentId', 'val':comment_id}}
        saved = Comment.get_one(query_keys)

        #update_attrs = ['publishStatus', 'body', 'contentId', 'profiles']
        upd_vals = {}
        for upd_attr in self.update_attrs:
            if upd_attr not in vals:
                continue

            if vals[upd_attr] == saved[upd_attr]:
                continue

            if upd_attr == 'contentId':
                vals['serviceIdContentId'] = '#'.join([self.service_id, vals['contentId']])

            if upd_attr == 'publishStatus':
                upd_vals['statusCreatedAt'] = '#'.join([vals[upd_attr], saved['createdAt']])

            upd_vals[upd_attr] = vals[upd_attr]

        self.debug_log({
            'func':'update_comment-10',
            'vals': vals,
            'upd_vals': upd_vals,
        })
        if len(upd_vals) == 0:
            self.debug_log({
                'func':'update_comment-0',
                'commentId': comment_id,
                'msg': 'Skipped for updated item not exists',
            })
            return

        if 'contentId' in upd_vals:
            res = Comment.update_pk_value(query_keys, upd_vals)
        else:
            res = Comment.update(query_keys, upd_vals, True)

        # Update comment count
        sid = self.service_id
        if 'contentId' in upd_vals:
            CommentCount.update_count(sid, saved['contentId'], saved['publishStatus'], True)
            ## Already updated count by Comment.update_pk_value
            #CommentCount.update_count(sid, upd_vals['contentId'], saved['publishStatus'])
        elif 'publishStatus' in upd_vals:
            CommentCount.update_count(sid, saved['contentId'], saved['publishStatus'], True)
            CommentCount.update_count(sid, saved['contentId'], upd_vals['publishStatus'])

        return res


    def set_saved_comment_ids(self):
        keys = {'p':{'key':'serviceId', 'val':self.service_id}}
        comments = Comment.get_all(keys, False, 'commentCreatedAtGsi', 0, ['commentId'])
        self.saved_comment_ids = [ comment['commentId'] for comment in comments ]


    def get_contentId_from_label(self, label):
        content_dict = find_dicts(self.content_list, 'label', label)
        return content_dict['id'] if content_dict else ''


    def check_file_size_limit(self, file_size):
        if int(file_size) > self.file_size_limit:
            raise InvalidValueError('File size is over limit: %s' % file_size)


    def debug_log(self, msg, level='info'):
        if not self.debug_log_enabled:
            return

        output_log(msg, level)


    @staticmethod
    def gen_comment_id(service_id, local_id):
        return '-'.join([service_id, local_id.zfill(5)])


    @staticmethod
    def ajust_date_format(value):
        date_str, time_str = value.split(' ')
        date_zfilled = date_to_zfill(date_str)

        if len(time_str.split(':')) == 2:
            time_str += ':00'

        return '%s %s' % (date_zfilled, time_str)


class InvalidValueError(Exception):
    pass


def handler(event=None, context=None):
    try:
        output_log('START: comment_importer.handler')
        output_log(['comment_importer.handler:event', event])

        s3_event = event['Records'][0]['s3']
        bucket_name = s3_event['bucket']['name']
        bucket_path = s3_event['object']['key']
        service_id = bucket_path.strip('/').split('/')[1]
        file_size = s3_event['object']['size']

        ci = CommentImporter(service_id)
        ci.main(bucket_name, bucket_path, file_size)

        output_log('END: comment_importer.handler: Success')
        return 'Success'

    except Exception as e:
        output_log(e, 'error')
        return 'END: comment_importer.handler: Error'
