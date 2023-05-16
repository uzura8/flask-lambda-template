from app.models.dynamodb.base import Base


class ShortenUrl(Base):
    table_name = 'shorten-url'
    public_attrs = [
        'urlId',
        'locationTo',
        'createdAt',
    ]
    response_attrs = public_attrs + []
    private_attrs = [
        'serviceId',
        'url',
        'isViaJumpPage',
        'paramKey',
        'paramValue',
        'name',
        'description',
        'createdBy',
    ]
    all_attrs = public_attrs + private_attrs


    @classmethod
    def query_pager(self, hkey=None, params=None):
        index = params.get('index')
        is_desc = params.get('order', 'asc') == 'desc'
        limit = params.get('count', 20)
        start_key = params.get('ExclusiveStartKey')

        table = self.get_table()

        key_cond_exps = []
        exp_attr_names = {}
        exp_attr_vals = {}
        option = {
            'ScanIndexForward': not is_desc,
            'Limit': limit,
        }
        if index:
            option['IndexName'] = index

        if hkey is not None:
            key_cond_exps.append('#hk = :hv')
            exp_attr_names['#hk'] = hkey['name']
            exp_attr_vals[':hv'] = hkey['value']

        if key_cond_exps:
            option['KeyConditionExpression'] = ' AND '.join(key_cond_exps)
            option['ExpressionAttributeNames'] = exp_attr_names
            option['ExpressionAttributeValues'] = exp_attr_vals

        if start_key:
            option['ExclusiveStartKey'] = start_key

        res = table.query(**option)
        items = res['Items']

        return {
            'items': items,
            'pagerKey': res['LastEvaluatedKey'] if 'LastEvaluatedKey' in res else None,
        }
