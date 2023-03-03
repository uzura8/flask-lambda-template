import os
import boto3
from app.common.date import utc_iso
from app.common.string import new_uuid
from pprint import pprint #!!!!!!!!!!!!!!!!


class Base():
    __abstract__ = True

    IS_LOCAL = os.getenv('IS_LOCAL', 'False').lower() == 'true'
    PRJ_PREFIX = os.environ['PRJ_PREFIX']

    reserved_values = None

    @classmethod
    def connect_dynamodb(self):
        if self.IS_LOCAL:
            dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
        else:
            dynamodb = boto3.resource('dynamodb')
        return dynamodb


    @classmethod
    def get_table(self, table_name=None):
        dynamodb = self.connect_dynamodb()
        table_name = self.get_table_name()
        return dynamodb.Table(table_name)


    @classmethod
    def get_table_name(self):
        return '-'.join([self.PRJ_PREFIX, self.table_name])


    @classmethod
    def prj_exps_str(self, is_public=True):
        attrs = self.public_attrs if is_public else self.all_attrs
        res = [ attr['key'] if isinstance(attr, dict) else attr for attr in attrs ]
        return ', '.join(res)


    @classmethod
    def to_response(self, item):
        res = {}
        for i in self.response_attrs:
            if isinstance(i, str):
                k = i
                l = i
            if isinstance(i, dict):
                k = i['key']
                l = i['label']

            if k in item:
                val = item.get(k)
                if val:
                    res[l] = val

        return res


    @classmethod
    def scan(self, options=None, is_return_raw=False):
        if options is None:
            options = {}
        table = self.get_table()
        res = table.scan(**options)

        if is_return_raw:
            return res

        return res.get('Items', [])


    @classmethod
    def get_all(self, keys, is_desc=False, index_name=None, limit=0, projections=None):
        table = self.get_table()
        option = {
            'ScanIndexForward': not is_desc,
        }
        if limit:
            option['Limit'] = limit

        if projections:
            if isinstance(projections, list):
                projections = ', '.join(projections)
            option['ProjectionExpression'] = projections

        if index_name:
            option['IndexName'] = index_name

        if not keys.get('p'):
            raise ModelInvalidParamsException("'p' is required on keys")

        key_cond_exps = ['#pk = :pk']
        exp_attr_names = {'#pk': keys['p']['key']}
        exp_attr_vals = {':pk': keys['p']['val']}

        if keys.get('s'):
            exp_attr_names['#sk'] = keys['s']['key']
            exp_attr_vals[':sk'] = keys['s']['val']
            key_cond_exps.append('#sk = :sk')

        option['KeyConditionExpression'] = ' AND '.join(key_cond_exps)
        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals
        res = table.query(**option)
        return res['Items'] if len(res['Items']) > 0 else []


    @classmethod
    def get_one(self, keys, is_desc=False, index_name=None, projections=None):
        items = self.get_all(keys, is_desc, index_name, 1, projections)
        return items[0] if len(items) > 0 else None


    @classmethod
    def get_all_by_pkey(self, pkeys, params=None, index_name=None, is_all_attr=True):
        table = self.get_table()

        if params and params.get('order') and not params.get('is_desc'):
            if params is None:
                params = {}
            params['is_desc'] = params.get('order') == 'desc'

        option = {'ScanIndexForward': not (params and  params.get('is_desc', False))}

        if params and params.get('count'):
            option['Limit'] = params['count']

        if index_name:
            option['IndexName'] = index_name

        key_cond_exp = '#pk = :pk'
        exp_attr_names = {'#pk': pkeys['key']}
        exp_attr_vals = {':pk': pkeys['val']}

        option['KeyConditionExpression'] = key_cond_exp
        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals
        res = table.query(**option)
        items = res.get('Items')
        if is_all_attr:
            return items

        return [ self.to_response(item) for item in items ]


    @classmethod
    def get_one_by_pkey(self, hkey_name, hkey_val, is_desc=False, index_name=None):
        table = self.get_table()
        option = {
            'ScanIndexForward': not is_desc,
            'Limit': 1,
        }
        if index_name:
            option['IndexName'] = index_name
        exp_attr_names = {}
        exp_attr_vals = {}
        exp_attr_names['#hk'] = hkey_name
        exp_attr_vals[':hv'] = hkey_val
        option['KeyConditionExpression'] = '#hk = :hv'
        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals
        res = table.query(**option)
        return res['Items'][0] if len(res['Items']) > 0 else None


    @classmethod
    def delete(self, key_dict):
        table = self.get_table()
        res = table.delete_item(
          Key=key_dict
        )
        return res


    @classmethod
    def get_reserved_values(self, attr):
        if not self.reserved_values:
            return []

        if attr not in self.reserved_values:
            return []

        return self.reserved_values[attr]


    @classmethod
    def check_set_reserved_value(self, vals, is_raise_exp=True):
        if not self.reserved_values:
            return False

        for attr in self.reserved_values:
            if attr not in vals:
                continue

            if vals[attr] in self.reserved_values[attr]:
                if is_raise_exp:
                    raise ModelInvalidParamsException('%s value is not allowed' % attr)
                else:
                    return True

        return False


    @classmethod
    def create(self, vals, uuid_name=None):
        if not vals.get('createdAt'):
            if vals.get('updatedAt'):
                vals['createdAt'] = vals['updatedAt']
            else:
                vals['createdAt'] = utc_iso(False, True)

        self.check_set_reserved_value(vals)

        if uuid_name:
            vals[uuid_name] = new_uuid()

        table = self.get_table()
        table.put_item(Item=vals)
        return vals


    @classmethod
    def update(self, query_keys, vals, is_update_time=False):
        self.check_set_reserved_value(vals)

        table = self.get_table()

        if is_update_time:
            vals['updatedAt'] = utc_iso(False, True)

        update_attrs = {}
        for key,val in vals.items():
            update_attrs[key] = { 'Value': val }

        update_keys = {}
        for key_type,key_dict in query_keys.items():
            key_name = key_dict['key']
            update_keys[key_name] = key_dict['val']
        res = table.update_item(
            Key=update_keys,
            AttributeUpdates=update_attrs,
        )
        items = self.get_one(query_keys)
        return items


    @classmethod
    def update_pk_value(self, current_keys, update_vals, is_update_time=False):
        item = self.get_one(current_keys)
        for attr, val in update_vals.items():
            item[attr] = val

        if is_update_time:
            item['updatedAt'] = utc_iso(False, True)

        key_dict = {}
        pkey = current_keys['p']['key']
        key_dict[pkey] = current_keys['p']['val']
        if 's' in current_keys:
            skey = current_keys['s']['key']
            key_dict[skey] = current_keys['s']['val']

        self.delete(key_dict)
        return self.create(item)


    @classmethod
    def batch_get_items(self, keys):
        dynamodb = self.connect_dynamodb()
        table_name = self.get_table_name()
        res = dynamodb.batch_get_item(
            RequestItems={
                table_name: {
                    'Keys': keys,
                    'ConsistentRead': True
                }
            },
            ReturnConsumedCapacity='TOTAL'
        )
        return res['Responses'][table_name]


    @classmethod
    def batch_save(self, items, pkeys=None, is_overwrite=False):
        table = self.get_table()
        overwrite_by_pkeys = pkeys if is_overwrite and pkeys else []
        with table.batch_writer(overwrite_by_pkeys=overwrite_by_pkeys) as batch:
            for item in items:
                #target_keys = {k: v for k, v in item.items() if k in pkeys or not pkeys}
                target_keys = {k: v for k, v in item.items()}
                batch.put_item(target_keys)


    @classmethod
    def batch_delete(self, items, pkeys=None):
        table = self.get_table()
        with table.batch_writer() as batch:
            for item in items:
                #target_keys = {k: v for k, v in item.items() if k in pkeys or not pkeys}
                target_keys = {k: v for k, v in item.items()}
                batch.delete_item(target_keys)


    @classmethod
    def truncate(self):
        table = self.get_table()
        delete_items = []
        params   = {}
        while True:
            res = table.scan(**params)
            delete_items.extend(res['Items'])
            if ('LastEvaluatedKey' in res):
                params['ExclusiveStartKey'] = res['LastEvaluatedKey']
            else:
                break

        key_names = [ x['AttributeName'] for x in table.key_schema ]
        delete_keys = [ { k:v for k,v in x.items() if k in key_names } for x in delete_items ]

        with table.batch_writer() as batch:
            for key in delete_keys:
                batch.delete_item(Key = key)


    @classmethod
    def query_loop_for_limit(self, option, target_count, pager_key, pager_keys, use_cate_filter=False):
        items_all = []
        loop_count = 0
        loop_count_max = 10
        need_count = target_count

        while loop_count < loop_count_max:
            adjust_count = self.get_ajust_count(need_count, use_cate_filter)
            option['Limit'] = need_count + adjust_count
            if pager_key:
                option['ExclusiveStartKey'] = pager_key

            items, pager_key = self.exe_query(option)

            is_break = False
            if len(items) < need_count and pager_key:
                need_count = need_count - len(items)
            else:
                is_break = True

            items_all.extend(items)

            if is_break:
                break

            loop_count += 1

        if len(items_all) > target_count:
            items_all = items_all[:target_count]
            pager_key = self.get_pager_key_from_list(items_all, pager_keys['pkey'],
                                         pager_keys['index_pkey'], pager_keys['index_skey'])

        return items_all, pager_key


    @classmethod
    def exe_query(self, option):
        table = self.get_table()
        res = table.query(**option)
        return res.get('Items', []), res.get('LastEvaluatedKey')


    @staticmethod
    def get_ajust_count(reqired_count, use_cate_filter=False):
        if use_cate_filter:
            if reqired_count < 10:
                adjust_count = 50
            elif reqired_count < 50:
                adjust_count = 100
            else:
                adjust_count = 300
        else:
            if reqired_count < 10:
                adjust_count = 20
            elif reqired_count < 50:
                adjust_count = 50
            else:
                adjust_count = 100

        return adjust_count


    @staticmethod
    def get_pager_key_from_list(items, pkey, index_pkey, index_skey):
        item = items[-1]
        return {
            pkey: item[pkey],
            index_pkey: item[index_pkey],
            index_skey: item[index_skey],
        }


class ModelInvalidParamsException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
