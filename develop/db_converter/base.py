import os
#import sys
import datetime
import configparser
import json
import decimal
from pathlib import Path
import pymysql.cursors
from pprint import pprint #!!!!!!!!!!!!!!!!

#parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#sys.path.append(parent_dir)
#
#from app.common.decimal_encoder import DecimalEncoder


class DbConverterBase():
    __abstract__ = True

    config = None
    connect = None
    cursor = None
    limit = 0
    offset = 0
    offset_max = 0 # On Development, Set this value
    service_id = ''
    service_label = ''
    user_id = ''
    category_exc_table = []
    tag_exc_table = []
    post_exc_table = []
    logs_dir = ''


    def __init__(self):
        self.set_conf()
        self.set_connect()
        self.make_logs_dir()


    def __del__(self):
        self.save_exc_tables()
        self.cursor.close()
        self.connect.close()


    def from_records(self, table, order_by='id'):
        params = (table, order_by, self.limit, self.offset)
        sql = 'SELECT * FROM %s ORDER BY %s LIMIT %s OFFSET %s' % params
        print(sql)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res


    def get_all(self, table, order_by='id'):
        params = (table, order_by)
        sql = 'SELECT * FROM %s ORDER BY %s' % params
        print(sql)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res


    def get_all_by_id(self, table, cond_val, cond_key='id'):
        params = (table, cond_key, cond_val)
        sql = 'SELECT * FROM %s WHERE %s = %s' % params
        print(sql)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res


    def get_category_slug_by_id(self, from_id, from_id_name='fromId'):
        if not self.category_exc_table:
            return ''

        items = [x for x in self.category_exc_table if x[from_id_name] == from_id]
        if not items:
            return ''

        return items[0].get('toSlug', '')


    def make_logs_dir(self):
        current = self.get_current_time()
        parent = Path(__file__).resolve().parent
        self.logs_dir = parent.joinpath('var/logs/%s' % current)
        os.mkdir(self.logs_dir)


    def save_exc_tables(self):
        self.save_exc_table('category', self.category_exc_table)
        self.save_exc_table('tag', self.tag_exc_table)
        self.save_exc_table('post', self.post_exc_table)


    def save_exc_table(self, table_name, data):
        path = '%s/%s.json' % (self.logs_dir, table_name)
        json_file = open(path, mode='w')
        json.dump(data, json_file, default=self.encode_decimal)
        json_file.close()


    def set_conf(self):
        self.config = configparser.ConfigParser()
        parent = Path(__file__).resolve().parent
        config_path = parent.joinpath('config.ini')
        self.config.read(config_path, encoding='utf-8')
        conf = self.config['CONVERT']
        self.limit = int(conf['limit'])
        self.user_id = conf['user_id_common']

        conf = self.config['SERVICE']
        self.service_id = conf['service_id']
        self.service_label = conf['service_label']


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
