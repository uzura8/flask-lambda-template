import os
import sys
import datetime
import configparser
import json
import decimal
import requests
from pathlib import Path
import pymysql.cursors

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

from app.common.log import output_log
from app.aws_s3_handler import AwsS3Handler


class DbConverterBase():
    __abstract__ = True

    config = None
    connect = None
    cursor = None
    converter_base_path = None
    limit = 0
    offset = 0
    s3handler = None
    service_id = ''
    service_label = ''
    service_base_url = ''
    media_s3_bucket_name = ''
    media_domain_before = ''
    media_base_url_before = ''
    media_domain_abolished = ''
    site_domain_before = ''
    site_base_url_after = ''
    allowed_image_sizes = ''
    user_id = ''
    category_exc_table = []
    tag_exc_table = []
    post_exc_table = []
    post_tag_exc_table = []
    post_group_exc_table = []
    file_exc_table = []
    file_not_exists = []
    file_related_others = []
    logs_dir = ''
    offset_max = 0 # On Development, Set this value


    def __init__(self):
        output_log('START: Convert')
        self.converter_base_path = Path(__file__).resolve().parent
        self.set_conf()
        self.set_connect()
        self.make_logs_dir()
        self.s3handler = AwsS3Handler(self.media_s3_bucket_name)


    def __del__(self):
        self.save_exc_tables()
        self.cursor.close()
        self.connect.close()
        output_log('END: Convert')


    def set_conf(self):
        self.config = configparser.ConfigParser()
        config_path = self.converter_base_path.joinpath('config.ini')
        self.config.read(config_path, encoding='utf-8')
        conf = self.config['CONVERT']
        self.limit = int(conf['limit'])
        self.user_id = conf['user_id_common']

        conf = self.config['SERVICE']
        self.service_id = conf['service_id']
        self.service_label = conf['service_label']
        self.media_domain_before = conf['media_domain_before']
        self.media_base_url_before = f'https://{self.media_domain_before}/gunma'
        self.media_domain_abolished = conf['media_domain_abolished']
        self.media_s3_bucket_name = conf['media_s3_bucket_name']
        self.allowed_image_sizes = conf['allowed_image_sizes']
        self.site_domain_before = conf['site_domain_before']
        self.site_base_url_after = conf['site_base_url_after']


    def from_records(self, table, order_by='id'):
        params = (table, order_by, self.limit, self.offset)
        sql = 'SELECT * FROM %s ORDER BY %s LIMIT %s OFFSET %s' % params
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res


    def get_all(self, table, order_by='id'):
        params = (table, order_by)
        sql = 'SELECT * FROM %s ORDER BY %s' % params
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res


    def get_all_where(self, table, wehre_cond, order_by='id'):
        params = (table, wehre_cond, order_by)
        sql = 'SELECT * FROM %s WHERE %s ORDER BY %s' % params
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res


    def get_all_by_id(self, table, cond_val, cond_key='id'):
        params = (table, cond_key, cond_val)
        sql = "SELECT * FROM %s WHERE %s = '%s'" % params
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res


    def get_category_by_from_id(self, from_id, from_id_name='fromId'):
        if not self.category_exc_table:
            return None

        items = [x for x in self.category_exc_table if x[from_id_name] == from_id]
        if not items:
            return None

        return items[0]


    def get_category_id_by_from_id(self, from_id, from_id_name='fromId'):
        item = self.get_category_by_from_id(from_id, from_id_name)
        if not item:
            return None

        return item.get('toId')


    def get_category_slug_by_id(self, from_id, from_id_name='fromId'):
        item = self.get_category_by_from_id(from_id, from_id_name)
        if not item:
            return None

        return item.get('toSlug', '')


    def get_is_unpublished_category(self, from_id, from_id_name='fromId'):
        item = self.get_category_by_from_id(from_id, from_id_name)
        if not item:
            return None

        return item.get('fromIsPrivate', '')


    def make_logs_dir(self):
        self.logs_dir = self.converter_base_path.joinpath('var/converteds')
        #os.mkdir(self.logs_dir)


    def save_exc_tables(self):
        self.save_exc_table('category', self.category_exc_table)
        self.save_exc_table('tag', self.tag_exc_table)
        self.save_exc_table('post', self.post_exc_table)
        self.save_exc_table('post_tag', self.post_tag_exc_table)
        self.save_exc_table('post_group', self.post_group_exc_table)
        self.save_exc_table('file', self.file_exc_table)
        self.save_exc_table('file_not_exists', self.file_not_exists)
        self.save_exc_table('file_related_others', self.file_related_others)


    def save_exc_table(self, table_name, data):
        path = '%s/%s.json' % (self.logs_dir, table_name)
        json_file = open(path, mode='w', encoding='utf-8')
        json.dump(data, json_file, default=self.encode_decimal)
        json_file.close()


    def load_exc_table_category(self):
        table_name = 'category'
        path = '%s/%s.json' % (self.logs_dir, table_name)
        with open(path, encoding='utf-8') as f:
            self.category_exc_table = json.load(f)


    def reset_file_exc_table(self):
        self.file_exc_table = []


    def get_file_by_url(self, url, save_path=None):
        res = requests.get(url, timeout=(5.0, 10.0)).content

        if save_path:
            abs_path = self.converter_base_path.joinpath(save_path)
            with open(abs_path, mode='wb') as f:
                f.write(res)

        return res


    def upload_media_to_s3(self, blob, upload_key, mimetype):
        self.s3handler.upload(blob, upload_key, mimetype)


    def set_connect(self):
        dbconf = self.config['DB']
        self.connect = pymysql.connect(host=dbconf['host'],
                                     user=dbconf['dbuser'],
                                     password=dbconf['password'],
                                     database=dbconf['dbname'],
                                     cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.connect.cursor()


    @staticmethod
    def get_current_time():
        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        now = datetime.datetime.now(JST)
        return now.strftime('%Y%m%d%H%M%S')


    @staticmethod
    def encode_decimal(o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)

            return int(o)

        return o
