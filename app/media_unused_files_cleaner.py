from app.aws_s3_handler import AwsS3Handler
from app.models.dynamodb import File
from app.common.site import media_bucket_file_path, media_bucket_file_dir
from app.common.date import get_calced_date_str
from app.common.log import output_log


class MediaUnusedFilesCleaner:
    s3handler = None
    debug_log_enabled = False
    limit = None
    targets = []
    scan_params = {}
    pager_key = None
    expired_at_for_reseved = None


    def __init__(self, bucket_name, expir_hours_for_reserved, limit=None, options=None):
        add_hour = expir_hours_for_reserved * -1
        self.expired_at_for_reseved = get_calced_date_str(None, None, hours=add_hour)
        #self.expired_at_for_reseved = get_calced_date_str(None, None, minutes=-5)
        if limit:
            self.limit = limit
        self.s3handler = AwsS3Handler(bucket_name)

        if options:
            if 'debug_log_enabled' in options:
                self.debug_log_enabled = options.get('debug_log_enabled')


    def __del__(self):
        pass


    def main(self):
        self.delete_files_by_status('removed')
        self.delete_files_by_status('reserved')


    def delete_files_by_status(self, status):
        pager_key = None
        is_scaned_all = False
        scan_option = self.get_scan_option(status, self.limit)
        while not is_scaned_all:
            items, pager_key = self.get_target_files(scan_option, pager_key)
            self.delete_files(items)

            if pager_key is None:
                is_scaned_all = True


    def get_scan_option(self, status, limit):
        if status == 'removed':
            return self.get_scan_option_for_removed(limit)

        if status == 'reserved':
            return self.get_scan_option_for_reserved(self.expired_at_for_reseved, limit)

        raise Exception('status is invalid')


    def delete_files(self, items):
        del_keys = []
        for item in items:
            self.delete_s3_objects_by_type(item)
            del_keys.append(item['fileId'])

        self.batch_delete_dynamodb_files(del_keys)


    def delete_s3_objects_by_type(self, item):
        sid = item['serviceId']
        fid = item['fileId']
        ftype = item['fileType']
        if ftype not in ['image', 'file']:
            raise Exception('fileType is invalid')

        if ftype == 'image':
            file_dir = media_bucket_file_dir(sid, ftype, fid)
            self.s3handler.delete_by_dir(file_dir)
            output_log(['delete_s3_objects_by_type:1', file_dir])
        else:
            file_path = media_bucket_file_path(sid, ftype, fid, item['mimeType'])
            self.s3handler.delete(file_path)
            output_log(['delete_s3_objects_by_type:2', file_path])


    @staticmethod
    def get_target_files(scan_option, pager_key=None):
        if pager_key:
            scan_option['ExclusiveStartKey'] = pager_key

        res = File.scan(scan_option, True)
        output_log(['get_target_files', scan_option, res.get('LastEvaluatedKey'), res['Count']])
        return res['Items'], res.get('LastEvaluatedKey')


    @staticmethod
    def get_scan_option_for_removed(limit=None):
        opt = {
            'FilterExpression': '#fs = :fs',
            'ExpressionAttributeNames': {'#fs':'fileStatus'},
            'ExpressionAttributeValues': {':fs':'removed'},
        }
        if limit:
            opt['Limit'] = limit

        return opt


    @staticmethod
    def get_scan_option_for_reserved(expired_at_for_reseved, limit=None):
        opt = {
            'FilterExpression': '#fs = :fs AND #ca < :ca',
            'ExpressionAttributeNames': {
                '#fs': 'fileStatus',
                '#ca': 'createdAt',
            },
            'ExpressionAttributeValues': {
                ':fs': 'reserved',
                ':ca': expired_at_for_reseved,
            },
        }
        if limit:
            opt['Limit'] = limit

        return opt


    @staticmethod
    def batch_delete_dynamodb_files(file_ids):
        keys = [{'fileId':fid} for fid in file_ids ]
        output_log(['batch_delete_dynamodb_files', keys])
        File.batch_delete(keys)
