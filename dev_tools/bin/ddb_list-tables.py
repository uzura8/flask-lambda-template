import os
from pprint import pprint
import boto3
from boto3.dynamodb.conditions import Key

IS_LOCAL = bool(os.environ.get('IS_LOCAL'))


class DynamoDBHandler:
    dynamodb = None
    tables = []


    def __init__(self, is_local=False):
        if is_local:
            self.dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
        else:
            self.dynamodb = boto3.resource('dynamodb')

        self.set_tables()


    def set_tables(self):
        self.tables = self.list_tables()


    def list_tables(self):
        table_list = self.dynamodb.tables.all()
        return [t.table_name for t in table_list]


    def get_table_name(self, table_name):
        table_name_real = '-'.join([os.environ['PRJ_PREFIX'], table_name])
        if table_name_real not in self.tables:
            raise Exception('Table name is invalid')
        return table_name_real


    def get_table(self, table_name):
        table_name_real = self.get_table_name(table_name)
        table = self.dynamodb.Table(table_name_real)
        return table


    def scan(self, table_name):
        table = self.get_table(table_name)
        return table.scan()


    def get_all_by_between(self, table_name, service_id, start, end):
        table = self.get_table(table_name)
        option = {
            'KeyConditionExpression':
                Key('serviceId').eq(service_id) & \
                Key('createdAt').between(start, end)
        }
        return table.query(**option)


    def get_all_by_lt(self, table_name, service_id, point):
        table = self.get_table(table_name)
        option = {
            'KeyConditionExpression':
                Key('serviceId').eq(service_id) & \
                Key('createdAt').lt(point)
        }
        return table.query(**option)


    def get_all_by_limit(self, table_name, limit):
        table = self.get_table(table_name)
        return table.scan(
            Limit=limit
        )


    def get_table_count(self, table_name):
        table = self.get_table(table_name)
        return table.item_count


ddh = DynamoDBHandler(IS_LOCAL)
tables = ddh.list_tables()
pprint(tables)
res = ddh.scan('vote-log')
pprint(res)
res = ddh.scan('vote-count')
pprint(res)
start = '2021-08-09T05:50:00.000000Z'
end = '2021-08-09T06:40:00.000000Z'
res = ddh.get_all_by_between('vote-log', 'fuga', start, end)
pprint(res)
res = ddh.get_all_by_lt('vote-log', 'fuga', end)
pprint(res)
res = ddh.get_table_count('vote-log')
pprint(res)
#res = ddh.get_all_by_limit('vote-log', 10)
#pprint(res)
res = ddh.scan('contact')
pprint(res)
