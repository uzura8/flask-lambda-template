from app.common.date import utc_iso
from app.common.string import new_uuid
from app.models.dynamodb import Base, ModelInvalidParamsException
from app.models.dynamodb.service import Service
from app.models.dynamodb.comment_count import CommentCount



class Comment(Base):
    table_name = 'comment'
    response_attr = [
    ]


    @classmethod
    def query_all_publish(self, service_id, content_id, params):
        index_name = 'statusCreatedAtGsi'
        table = self.get_table()
        until_time = params.get('untilTime', '')
        since_time = params.get('sinceTime', '')
        is_desc = params.get('order', 'asc') == 'desc'
        limit = params.get('count', 20)
        category = params.get('category')

        sort_key = 'createdAt'
        exp_attr_names = {}
        exp_attr_vals = {}
        key_conds = ['#si = :si']
        option = {
            'IndexName': index_name,
            'ScanIndexForward': not is_desc,
            'Limit': limit,
        }
        exp_attr_names['#si'] = 'serviceIdContentId'
        exp_attr_vals[':si'] = '#'.join([service_id, content_id])

        key_conds.append('begins_with(#sp, :sp)')
        exp_attr_names['#sp'] = 'statusCreatedAt'
        exp_attr_vals[':sp'] = 'publish'

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

        if category:
            cond = '#ct = :ct'
            exp_attr_names['#ct'] = 'category'
            exp_attr_vals[':ct'] = category
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
        items = result.get('Items', [])[:limit]

        return items


    @classmethod
    def create(self, vals):
        service_id = vals.get('serviceId')
        if not service_id:
            raise ModelInvalidParamsException('serviceId is required')

        if not Service.check_exists(service_id):
            raise ModelInvalidParamsException('serviceId not exists')

        time = utc_iso(False, True)

        required_attrs = ['contentId']
        for attr in required_attrs:
            if attr not in vals or len(vals[attr].strip()) == 0:
                raise ModelInvalidParamsException("Argument '%s' requires values" % attr)
        content_id = vals['contentId']

        status = vals['status']
        table = self.get_table()
        item = {
            'commentId': new_uuid(),
            'serviceId': service_id,
            'contentId': content_id,
            'serviceIdContentId': '#'.join([service_id, content_id]),
            'createdAt': time,
            'body': vals['body'],
            'publishStatus': status,
            'category': vals['category'],
            'statusCreatedAt': '#'.join([status, time]),
        }
        table.put_item(Item=item)
        CommentCount.update_count(service_id, content_id, status, time)

        return item
