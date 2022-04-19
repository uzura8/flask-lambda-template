from boto3.dynamodb.conditions import Key
from app.common.date import utc_iso
from app.models.dynamodb.base import Base
from app.models.dynamodb.tag import Tag


class PostTag(Base):
    table_name = 'post-tag'
    response_attr = [
    ]


    @classmethod
    def get_all_by_post_id(self, post_id, with_tags=False, for_response=True):
        table = self.get_table()
        res = table.query(
            KeyConditionExpression=Key('postId').eq(post_id),
            ScanIndexForward=True
        )
        items = res.get('Items', [])
        if not items:
            return []

        if not with_tags:
            return [ self.to_response(i) for i in items ] if for_response else items

        keys = []
        for item in items:
            keys.append({'tagId':item['tagId']})
        items = Tag.batch_get_items(keys)
        return [ Tag.to_response(i) for i in items ] if for_response else items


    @classmethod
    def query_all_by_tag_id(self, tag_id, params):
        table = self.get_table()
        until_time = params.get('untilTime', '')
        since_time = params.get('sinceTime', '')
        is_desc = params.get('order', 'asc') == 'desc'
        limit = params.get('count', 20)

        status = 'publish'
        sort_key = 'publishAt'
        prj_exps = ['postId', 'statusPublishAt']
        exp_attr_names = {}
        exp_attr_vals = {}
        key_conds = ['#ti = :ti']
        option = {
            'IndexName': 'postsByTagGsi',
            'ProjectionExpression': ', '.join(prj_exps),
            'ScanIndexForward': not is_desc,
            'Limit': limit,
        }
        exp_attr_names['#ti'] = 'tagId'
        exp_attr_vals[':ti'] = tag_id

        current = utc_iso(False, True)
        if not until_time or until_time > current:
            until_time = current

        key_conds.append('begins_with(#sp, :sp)')
        exp_attr_names['#sp'] = 'statusPublishAt'
        exp_attr_vals[':sp'] = status

        filter_exps = []
        if since_time:
            cond = '#st > :st'
            exp_attr_names['#st'] = sort_key
            exp_attr_vals[':st'] = since_time
            filter_exps.append(cond)

        if until_time:
            cond = '#ut < :ut'
            exp_attr_names['#ut'] = sort_key
            exp_attr_vals[':ut'] = until_time
            filter_exps.append(cond)

        filter_exps_str = ' AND '.join(filter_exps) if filter_exps else ''
        filter_exp = ''
        if filter_exps_str:
            filter_exp += filter_exps_str

        if filter_exp:
            option['FilterExpression'] = filter_exp
            option['Limit'] += 50

        option['KeyConditionExpression'] = ' AND '.join(key_conds)
        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals
        result = table.query(**option)

        return result.get('Items', [])[:limit]
