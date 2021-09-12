import os
from dynamodb import dynamodb


class Base():
    __abstract__ = True

    PRJ_PREFIX = os.environ['PRJ_PREFIX']
    ACCEPT_SERVICE_IDS = os.environ.get('ACCEPT_SERVICE_IDS', '').split(',')


    @classmethod
    def get_table(self):
        return dynamodb.Table('-'.join([self.PRJ_PREFIX, self.table_name]))
