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
    offset_max = 20
    service_id = ''
    service_label = ''


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


    def set_conf(self):
        self.config = configparser.ConfigParser()
        parent = Path(__file__).resolve().parent
        config_path = parent.joinpath('config.ini')
        self.config.read(config_path, encoding='utf-8')
        conf = self.config['CONVERT']
        self.limit = int(conf['limit'])

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
