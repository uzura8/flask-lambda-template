import os
import boto3
from app.common.date import utc_iso
from app.common.string import new_uuid


class Base():
    __abstract__ = True

    IS_LOCAL = bool(os.environ.get('IS_LOCAL'))
    PRJ_PREFIX = os.environ['PRJ_PREFIX']


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
    def scan(self, options=None):
        if not options:
            options = {}
        table = self.get_table()
        res = table.scan(**options)
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
    def get_all_by_pkey(self, pkeys, params=None, index_name=None):
        table = self.get_table()
        option = {'ScanIndexForward': not (params and  params.get('is_desc', False))}

        if params and params.get('count'):
            option['limit'] = params['count']

        if index_name:
            option['IndexName'] = index_name

        key_cond_exp = '#pk = :pk'
        exp_attr_names = {'#pk': pkeys['key']}
        exp_attr_vals = {':pk': pkeys['val']}

        option['KeyConditionExpression'] = key_cond_exp
        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals
        res = table.query(**option)

        return res.get('Items')


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
    def create(self, vals, uuid_name=None):
        if not vals.get('createdAt'):
            if vals.get('updatedAt'):
                vals['createdAt'] = vals['updatedAt']
            else:
                vals['createdAt'] = utc_iso(False, True)

        if uuid_name:
            vals[uuid_name] = new_uuid()

        table = self.get_table()
        table.put_item(Item=vals)
        return vals


    @classmethod
    def update(self, query_keys, vals, is_update_time=False):
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


class ModelInvalidParamsException(Exception):
    pass
