from io import StringIO
import csv
import os
import datetime
from pytz import timezone
import boto3
from boto3.dynamodb.conditions import Key
from app.dynamodb import dynamodb
from app.common.date import utc_iso


class VoteLogBackupHandler:
    table = None
    s3 = None
    bucket_name = None
    service_ids = []
    threshold_days_older_than = 1
    threshold_counts_to_backup = None
    threshold_datetime = None
    tmp_csv_path = '/tmp/vote-log.csv'

    def __init__(self):
        PRJ_PREFIX = os.environ.get('PRJ_PREFIX')
        VOTE_LOG_TABLE = '-'.join([PRJ_PREFIX, 'vote-log'])
        self.table = dynamodb.Table(VOTE_LOG_TABLE)

        self.bucket_name = os.environ.get('S3_BUCKET')
        self.s3 = boto3.resource('s3')

        self.threshold_days_older_than =\
                int(os.environ.get('BACKUP_VOTE_LOG_THRESHOLD_DAYS_OLDER_THAN', 1))
        self.threshold_counts_to_backup = {
            'all': int(os.environ.get('BACKUP_VOTE_LOG_COUNT_FOR_ALL')),
            'each_service': int(os.environ.get('BACKUP_VOTE_LOG_COUNT_FOR_EACH_SERVICE')),
        }
        self.service_ids = os.environ.get('ACCEPT_SERVICE_IDS', '').split(',')
        self.set_threshold_datetime()
        print('Start Backup')


    def __del__(self):
        print('End Backup')


    def backup_to_s3(self):
        if not self.is_require_to_backup():
            print('Stop this task for less items')
            return

        for sid in self.service_ids:
            self.backup_to_s3_each_service(sid)


    def backup_to_s3_each_service(self, service_id):
        resp = self.get_items_before_created(service_id, self.threshold_datetime)
        if resp['Count'] < self.threshold_counts_to_backup['each_service']:
            print('Skip each backup of {} for less items'.format(service_id))
            return

        csv_data = self.conv_to_csv(resp['Items'])
        self.put_to_s3(service_id, csv_data)

        count = 0
        for item in resp['Items']:
            self.delete_item(item['serviceId'], item['createdAt'])
            count += 1
        if count > 0:
            print('Deleted {} items of {}.'.format(count, service_id))


    def put_to_s3(self, sid, data):
        path = self.get_file_path(sid)
        obj = self.s3.Object(self.bucket_name, path)
        res = obj.put(Body = data)
        print('Put items to S3 bucket {}/{}.'.format(self.bucket_name, path))
        return res


    @staticmethod
    def conv_to_csv(items):
        rows = ''
        fields = ['contentId', 'createdAt', 'ip', 'serviceId', 'ua', 'voteType'] # header
        with StringIO() as bs:
            writer = csv.DictWriter(bs, fieldnames=fields)
            writer.writeheader()
            for item in items:
                writer.writerow(item)
            rows = bs.getvalue()
        return rows


    @staticmethod
    def get_file_path(sid):
        dir_name = 'vote_logs'
        time_str = utc_iso(False, True)
        return '{}/{}_{}.csv'.format(dir_name, sid, time_str)


    def is_require_to_backup(self):
        return self.get_count() > self.threshold_counts_to_backup['all']


    def set_threshold_datetime(self):
        dt = datetime.datetime.now() - datetime.timedelta(days=self.threshold_days_older_than)
        self.threshold_datetime = utc_iso(True, True, dt.astimezone(timezone('UTC')))


    def get_count(self):
        return self.table.item_count


    def get_items_before_created(self, service_id, created_at):
        option = {
            'KeyConditionExpression':
                Key('serviceId').eq(service_id) & \
                Key('createdAt').lt(created_at)
        }
        return self.table.query(**option)


    def delete_item(self, service_id, created_at):
        return self.table.delete_item(
            Key={
                'serviceId': service_id,
                'createdAt': created_at,
            },
        )


def main(ev = None, context = None):
    vh = VoteLogBackupHandler()
    vh.backup_to_s3()


if __name__ == '__main__':
    main()
