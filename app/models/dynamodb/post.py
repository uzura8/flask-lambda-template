from boto3.dynamodb.conditions import Key
from app.common.date import utc_iso, iso_offset2utc
from app.common.string import new_uuid
from app.models.dynamodb.base import Base
from app.models.dynamodb.category import Category


class Post(Base):
    table_name = 'post'
    response_attr = [
    ]


    @classmethod
    def query_all(self, index_name, service_id, params):
        table = self.get_table()

        status = 'publish' if params.get('publish', False) else 'unpublish'
        until_time = params.get('untilTime', '')
        since_time = params.get('sinceTime', '')
        is_desc = params.get('order', 'asc') == 'desc'
        limit = params.get('count', 5)
        cate_slugs = params.get('categories', [])

        exp_attr_names = {}
        exp_attr_vals = {}
        option = {
            'IndexName': index_name,
            'ProjectionExpression': 'title, id, slug, body, publishAt, categorySlug',
            'KeyConditionExpression': '#si = :si AND begins_with(#sp, :sp)',
            'ScanIndexForward': not is_desc,
            'Limit': limit,
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

        if cate_slugs:
            filter_exp_cids = []
            for i, cid in enumerate(cate_slugs):
                val_name = 'cid' + str(i)
                filter_exp_cids.append('#{v} = :{v}'.format(v=val_name))
                exp_attr_names['#{v}'.format(v=val_name)] = 'categorySlug'
                exp_attr_vals[':{v}'.format(v=val_name)] = cid
            if filter_exp:
                filter_exp = '{} AND ({})'.format(filter_exp, ' OR '.join(filter_exp_cids))
            else:
                filter_exp = ' OR '.join(filter_exp_cids)

        if filter_exp:
            option['FilterExpression'] = filter_exp
            option['Limit'] += 50

        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals
        result = table.query(**option)
        items = result.get('Items', [])[:limit]
        return items


    #@classmethod
    #def get_all_for_published(self, service_id):
    #    table = self.get_table()
    #    res = table.query(
    #        IndexName='gsi-list-all',
    #        ProjectionExpression='title, categorySlug, isPublish, id, slug, serviceId, publishAt',
    #        KeyConditionExpression=Key('serviceId').eq(service_id)\
    #                & Key('statusPublishAt').begins_with('publish#'),
    #        ScanIndexForward=False
    #    )
    #    return res['Items'] if 'Items' in res and res['Items'] else []


    @classmethod
    def get_one_by_slug(self, service_id, slug, with_cate=False):
        table = self.get_table()
        res = table.query(
            ProjectionExpression='title, id, slug, body, publishAt, categorySlug',
            KeyConditionExpression=Key('serviceIdSlug').eq('#'.join([service_id, slug])),
        )
        if 'Items' not in res or not res['Items']:
            return None

        item = res['Items'][0]
        if with_cate and 'categorySlug' in item and item['categorySlug']:
            item['category'] = Category.get_one_by_slug(service_id, item['categorySlug'],
                                                        True, False, True)

        return item


    @classmethod
    def create(self, service_id, kwargs):
        if service_id not in self.ACCEPT_SERVICE_IDS:
            raise ValueError('service_id is invalid')

        time = utc_iso(False, True)
        is_publish = kwargs['publish']\
                if 'publish' in kwargs and int(kwargs['publish']) == 1 else False
        status = 'publish' if is_publish else 'unpublish'

        if 'publishAt' in kwargs and kwargs['publishAt']:
            publish_at = iso_offset2utc(kwargs['publishAt'], True)

        else:
            publish_at = time

        required_attrs = ['slug', 'category', 'title']
        for attr in required_attrs:
            if attr not in kwargs or len(kwargs[attr].strip()) == 0:
                raise ValueError("Argument '%s' requires values" % attr)

        slug = kwargs['slug']
        cate_slug = kwargs['category']

        table = self.get_table()
        item = {
            'id': new_uuid(),
            'createdAt': time,
            'updatedAt': time,
            'serviceId': service_id,
            'slug': slug,
            'isPublish': is_publish,
            'publishAt': publish_at,
            'categorySlug': cate_slug,
            'title': kwargs['title'],
            'body': kwargs['body'],
            'serviceIdSlug': '#'.join([service_id, slug]),
            'statusPublishAt': '#'.join([status, publish_at]),
        }
        table.put_item(Item=item)
        return item
