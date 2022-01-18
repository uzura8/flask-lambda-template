import os
import re
from datetime import datetime, timezone
from pprint import pprint
import boto3
from boto3.dynamodb.conditions import Key, Attr

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


    def query_all(self, table_name, index_name, service_id, params):
        status = 'publish' if params.get('publish', False) else 'unpublish'
        until_time = params.get('untilTime', '')
        since_time = params.get('sinceTime', '')
        is_desc = params.get('order', 'asc') == 'desc'
        limit = int(params.get('limit', 3))
        cate_ids = params.get('categoryIds', [])

        table = self.get_table(table_name)
        exp_attr_names = {}
        exp_attr_vals = {}
        option = {
            'IndexName': index_name,
            'KeyConditionExpression': '#si = :si AND begins_with(#sp, :sp)',
            'ScanIndexForward': not is_desc,
            'Limit': 50,
        }
        exp_attr_names['#si'] = 'serviceId'
        exp_attr_names['#sp'] = 'statusPublishAt'
        exp_attr_vals[':si'] = service_id
        exp_attr_vals[':sp'] = status

        filter_exp = ''
        if since_time:
            filter_exp += '#st > :st'
            exp_attr_names['#st'] = 'publishAt'
            exp_attr_vals[':st'] = since_time

        if until_time:
            if filter_exp:
                filter_exp += ' AND '
            filter_exp += '#ut < :ut'
            exp_attr_names['#ut'] = 'publishAt'
            exp_attr_vals[':ut'] = until_time

        if cate_ids:
            filter_exp_cids = []
            for i, cid in enumerate(cate_ids):
                val_name = 'cid' + str(i)
                filter_exp_cids.append('#{v} = :{v}'.format(v=val_name))
                exp_attr_names['#{v}'.format(v=val_name)] = 'categoryId'
                exp_attr_vals[':{v}'.format(v=val_name)] = cid
            if filter_exp:
                filter_exp = '{} AND ({})'.format(filter_exp, ' OR '.join(filter_exp_cids))
            else:
                filter_exp = ' OR '.join(filter_exp_cids)

        if filter_exp:
            option['FilterExpression'] = filter_exp
            option['ExpressionAttributeNames'] = exp_attr_names
            option['ExpressionAttributeValues'] = exp_attr_vals

        result = table.query(**option)
        items = result.get('Items', [])[:limit]
        return items


    def query_with_filter_cate(self, table_name, service_id, status):
        table = self.get_table(table_name)
        return table.query(
            IndexName="gsi-list-all",
            KeyConditionExpression=Key('serviceId').eq(service_id) & Key('statusPublishAt').begins_with(status),
            #FilterExpression=Attr('publishAt').gt('2021-09-08T04:19:13.008277Z'),
            #FilterExpression=(Attr('categoryId').eq('cate02') | Attr('categoryId').eq('cate03'))\
            #        & Attr('publishAt').gt('publish#2021-09-08T04:19:12.531212Z'),
            FilterExpression=(Attr('categoryId').eq('cate01') | Attr('categoryId').eq('cate03')) & Attr('publishAt').gt('2021-09-08T04:19:13.008277Z'),
            ScanIndexForward=True,
            Limit=50
        )


    def query_with_filter_pks(self, table_name, service_id, status):
        table = self.get_table(table_name)
        return table.query(
            IndexName="gsi-list-all",
            KeyConditionExpression=Key('serviceId').eq(service_id) & Key('statusPublishAt').begins_with(status),
            #FilterExpression=Attr('publishAt').gt('2021-09-08T04:19:13.008277Z'),
            #FilterExpression=(Attr('categoryId').eq('cate02') | Attr('categoryId').eq('cate03'))\
            #        & Attr('publishAt').gt('publish#2021-09-08T04:19:12.531212Z'),
            #FilterExpression=(Attr('categoryId').eq('cate01') | Attr('categoryId').eq('cate03')) & Attr('publishAt').gt('2021-09-08T04:19:13.008277Z'),
            FilterExpression=(
                Attr('id').eq('01ff1vdprsvkktp2xvsr50002g')
                | Attr('id').eq('01ff1vdpn260jwb8e1n1kakzm8')
                | Attr('id').eq('01ff1vdph3weva0afxkgzg2sxq')
                | Attr('id').eq('01ff1t36fj472zbngp3p419x48')
                | Attr('id').eq('01ff1vdppy3v94bwjhd2f80emd')
                | Attr('id').eq('01ff1t35c2c6cxhr42mx9091zf')
                | Attr('id').eq('01ff1t356ffpg3nggt0ks12px5')
                | Attr('id').eq('01ff1t34z3xtsgnjt5v7dg5hgd')
            ) & Attr('publishAt').gt('2021-09-08T04:19:13.008277Z'),
            ScanIndexForward=True,
            Limit=50
        )


    def get_table_count(self, table_name):
        table = self.get_table(table_name)
        return table.item_count


    def batch_get_items(self, table_name, keys):
        table = self.get_table_name(table_name)
        response = self.dynamodb.batch_get_item(
            RequestItems={
                table: {
                    'Keys': keys,
                    'ConsistentRead': True
                }
            },
            ReturnConsumedCapacity='TOTAL'
        )
        return response


    def get_category_by_slug(self, table_name, service_id, slug):
        table = self.get_table('category')
        res = table.query(
            IndexName='gsi-one-by-slug',
            #ProjectionExpression='title, categoryId, isPublish, id, slug, serviceId, publishAt',
            KeyConditionExpression=Key('serviceIdSlug').eq('#'.join([service_id, slug])),
        )
        if 'Items' not in res or not res['Items']:
            return None

        item = res['Items'][0]
        parent_ids = item['parentPath'].split('#')
        if len(parent_ids) == 1:
            item['parents'] = []
        else:
            parents = self.get_cates_by_ids(parent_ids)
            item['parents'] = parents

        return item


    def get_cates_by_ids(self, ids):
        keys = []
        for cate_id in ids:
            keys.append({'id':int(cate_id)})
        pprint(3333333) #!!!!!!!!!!!!!!!!
        pprint(keys) #!!!!!!!!!!!!!!!!
        res = self.batch_get_items('category', keys)
        pprint(res) #!!!!!!!!!!!!!!!!
        return res['Items'][0] if 'Items' in res and res['Items'] else None


ddh = DynamoDBHandler(IS_LOCAL)
#tables = ddh.list_tables()
#pprint(tables)
#res = ddh.scan('vote-log')
#pprint(res)
#res = ddh.scan('vote-count')
#pprint(res)
#start = '2021-08-09T05:50:00.000000Z'
#end = '2021-08-09T06:40:00.000000Z'
#res = ddh.get_all_by_between('vote-log', 'fuga', start, end)
#pprint(res)
#res = ddh.get_all_by_lt('vote-log', 'fuga', end)
#pprint(res)
#res = ddh.get_table_count('vote-log')
#pprint(res)
##res = ddh.get_all_by_limit('vote-log', 10)
##pprint(res)
#res = ddh.scan('contact')
#pprint(res)
#res = ddh.scan('post')
#pprint(res)
#
##keys = [
##    {'serviceIdSlug': 'hoge#info01'},
##    {'serviceIdSlug': 'hoge#info03'},
##    {'serviceIdSlug': 'hoge#info05'},
##    {'serviceIdSlug': 'hoge#info07'},
##    {'serviceIdSlug': 'hoge#info09'},
##]
##res = ddh.batch_get_items('post', keys)
##pprint(res)
##res = ddh.query_all('post', 'hoge', 'publish')
##pprint(res)
#res = ddh.query_with_filter_cate('post', 'hoge', 'publish')
#pprint(res)
#res = ddh.query_with_filter_pks('post', 'hoge', 'publish')
#pprint(res)

params = {
    'publish': True,
    'limit': 5,
    'order': 'desc',
    'sinceTime': '2021-09-12T00:41:48Z',
    'categoryIds': ['cate01', 'cate03'],
}
res = ddh.query_all('post', 'gsi-list-all', 'hoge', params)
pprint(res)
res = ddh.scan('site-config')
pprint(res)
res = ddh.scan('category')
pprint(res)
res = ddh.get_category_by_slug('category', 'hoge', 'tama-shi')
pprint(res)
