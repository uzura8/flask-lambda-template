import os
import boto3
from pprint import pprint #!!!!!!!!!!!!!!!!

TABLE_NAME = 'users'
USERS_TABLE = '-'.join([os.environ['PRJ_PREFIX'], TABLE_NAME])
IS_LOCAL = bool(os.environ.get('IS_LOCAL'))


class DynamoDBHandler:
    dynamodb = None
    tables = []


    def __init__(self, is_local=False):
        if IS_LOCAL:
            self.dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
        else:
            self.dynamodb = boto3.resource('dynamodb')

        self.set_tables()


    def set_tables(self):
        self.tables = self.list_tables()


    def list_tables(self):
        table_list = self.dynamodb.tables.all()
        return [t.table_name for t in table_list]


    def get_table(self, table_name):
        table_name_real = '-'.join([os.environ['PRJ_PREFIX'], table_name])
        if table_name_real not in self.tables:
            raise Exception('Table name is invalid')

        table = self.dynamodb.Table(table_name_real)
        return table


    def scan(self, table_name):
        table = self.get_table(table_name)
        return table.scan()


ddh = DynamoDBHandler(IS_LOCAL)
tables = ddh.list_tables()
pprint(tables) #!!!!!!!!!!!!
res = ddh.scan('users')
pprint(res) #!!!!!!!!!!!!
