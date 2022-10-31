import configparser
from pathlib import Path
import pymysql.cursors


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
    category_table = []
    tag_table = []
    post_table = []


    def __init__(self):
        self.set_conf()
        self.set_connect()


    def __del__(self):
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


    def get_category_slug_by_id(self, from_id, from_id_name='fromId'):
        if not self.category_table:
            return ''

        items = [x for x in self.category_table if x[from_id_name] == from_id]
        if not items:
            return ''

        return items[0].get('toSlug', '')
