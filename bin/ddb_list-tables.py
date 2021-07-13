import os
import boto3
from pprint import pprint #!!!!!!!!!!!!!!!!

USERS_TABLE = os.environ['USERS_TABLE']
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


    def check_table_name(self, table_name):
        if table_name not in self.tables:
            raise Exception('Table name is invalid')

        return True


    def scan(self, table_name):
        self.check_table_name(table_name)
        table = self.dynamodb.Table(table_name)
        res = table.scan()
        return res


ddh = DynamoDBHandler(IS_LOCAL)
tables = ddh.list_tables()
pprint(tables) #!!!!!!!!!!!!
res = ddh.scan('users-table-dev')
pprint(res) #!!!!!!!!!!!!
