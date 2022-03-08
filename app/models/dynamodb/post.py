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
    def query_all(self, index_name, service_id, params, with_cate=False):
        table = self.get_table()
        status = params.get('status')
        until_time = params.get('untilTime', '')
        since_time = params.get('sinceTime', '')
        is_desc = params.get('order', 'asc') == 'desc'
        limit = params.get('count', 5)
        cate_slugs = params.get('categories', [])

        sort_key = 'createdAt' if index_name == 'createdAtGsi' else 'publishAt'
        prj_exps = ['title', 'id', 'slug', 'body', 'publishAt', 'updatedAt',
                            'categorySlug', 'postStatus', 'createdAt']
        exp_attr_names = {}
        exp_attr_vals = {}
        key_conds = ['#si = :si']
        option = {
            'IndexName': index_name,
            'ProjectionExpression': ', '.join(prj_exps),
            #'KeyConditionExpression': '#si = :si AND begins_with(#sp, :sp)',
            'ScanIndexForward': not is_desc,
            'Limit': limit,
        }
        exp_attr_names['#si'] = 'serviceId'
        exp_attr_vals[':si'] = service_id

        if status:
            key_conds.append('begins_with(#sp, :sp)')
            exp_attr_names['#sp'] = 'statusPublishAt'
            exp_attr_vals[':sp'] = status
        option['KeyConditionExpression'] = ' AND '.join(key_conds)

        filter_exp = ''
        if since_time:
            filter_exp += '#st > :st'
            exp_attr_names['#st'] = sort_key
            exp_attr_vals[':st'] = since_time

        if until_time:
            if filter_exp:
                filter_exp += ' AND '
            filter_exp += '#ut < :ut'
            exp_attr_names['#ut'] = sort_key
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

        if with_cate:
            for idx, item in enumerate(items):
                cate = Category.get_one_by_slug(service_id, item['categorySlug'],
                                                            False, False, True)
                items[idx]['category'] = cate

        return items


    #@classmethod
    #def get_all_for_published(self, service_id):
    #    table = self.get_table()
    #    res = table.query(
    #        IndexName='statusPublishAtGsi',
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
            ProjectionExpression='title, id, slug, body, publishAt, updatedAt, categorySlug, postStatus',
            KeyConditionExpression=Key('serviceIdSlug').eq('#'.join([service_id, slug])),
        )
        if 'Items' not in res or not res['Items']:
            return None

        item = res['Items'][0]
        if with_cate and item.get('categorySlug'):
            item['category'] = Category.get_one_by_slug(service_id, item['categorySlug'],
                                                        True, False, True)

        return item


    @classmethod
    def create(self, service_id, kwargs):
        if service_id not in self.ACCEPT_SERVICE_IDS:
            raise ValueError('service_id is invalid')

        status = kwargs.get('status') or kwargs.get('postStatus')
        if status not in ['publish', 'unpublish']:
            raise ValueError('status is invalid')
        is_publish = status == 'publish'

        time = utc_iso(False, True)

        publish_at = ''
        if kwargs.get('publishAt'):
            publish_at = iso_offset2utc(kwargs['publishAt'], True)
        elif is_publish:
            publish_at = time

        required_attrs = ['slug', 'category', 'title']
        for attr in required_attrs:
            if attr not in kwargs or len(kwargs[attr].strip()) == 0:
                raise ValueError("Argument '%s' requires values" % attr)

        slug = kwargs['slug']
        cate_slug = kwargs['category']

        table = self.get_table()
        item = {
            #'id': new_uuid(),
            'createdAt': time,
            'updatedAt': time,
            'serviceId': service_id,
            'slug': slug,
            'publishAt': publish_at,
            'categorySlug': cate_slug,
            'title': kwargs['title'],
            'body': kwargs['body'],
            'serviceIdSlug': '#'.join([service_id, slug]),
            'postStatus': status,
            'statusPublishAt': '#'.join([status, publish_at]),
        }
        table.put_item(Item=item)
        return item


    @classmethod
    def update(self, service_id, slug, vals):
        if service_id not in self.ACCEPT_SERVICE_IDS:
            raise ValueError('service_id is invalid')

        time = utc_iso(False, True)
        saved = self.get_one_by_slug(service_id, slug, True)
        if not saved:
            raise ValueError('Slug is invalid')

        slug_upd = vals.get('slug')
        if slug_upd and slug_upd != saved['slug']:
            if Post.get_one_by_slug(service_id, slug_upd):
                raise ValueError('Slug already used')
        else:
            slug_upd = None

        if slug_upd:
            copied = saved
            for attr, val in vals.items():
                copied[attr] = val
            copied['slug'] = slug_upd
            create_res = self.create(service_id, copied)
            delete_res = self.delete({'serviceIdSlug': '#'.join([service_id, slug])})
            return create_res

        cate_slug_upd = vals.get('category')
        if cate_slug_upd and cate_slug_upd != saved['categorySlug']:
            cate_upd = Category.get_one_by_slug(service_id, cate_slug_upd)
            if not cate_upd:
                raise ValueError('Category not exists', 400)
        else:
            cate_slug_upd = None

        status_upd = vals.get('status')
        if status_upd:
            if status_upd not in ['publish', 'unpublish']:
                raise ValueError('status is invalid')

            if status_upd == saved['postStatus']:
                status_upd = None

        is_published = status_upd and status_upd == 'publish'

        publish_at_upd = vals.get('publishAt', '')
        if publish_at_upd and publish_at_upd != saved['publishAt']:
            publish_at_upd = iso_offset2utc(vals['publishAt'], True)
        elif is_published:
            publish_at_upd = time

        table = self.get_table()
        exp_items = []
        exp_vals = {}

        if slug_upd:
            exp_items.append('slug=:slug')
            exp_vals[':slug'] = slug_upd
            exp_items.append('serviceIdSlug=:sis')
            exp_vals[':sis'] = '#'.join([service_id, slug_upd])

        if cate_slug_upd:
            exp_items.append('categorySlug=:cates')
            exp_vals[':cates'] = cate_slug_upd

        if status_upd:
            exp_items.append('postStatus=:ps')
            exp_vals[':ps'] = status_upd
            exp_items.append('statusPublishAt=:spa')
            exp_vals[':spa'] = '#'.join([status_upd, publish_at_upd])

        if publish_at_upd:
            exp_items.append('publishAt=:pa')
            exp_vals[':pa'] = publish_at_upd

        attrs = ['title', 'body']
        for attr in attrs:
            val = vals.get(attr)
            if val is None or val == saved.get(attr):
                continue

            exp_items.append('%s=:%s' % (attr, attr))
            exp_vals[':' + attr] = val

        if not exp_items:
            return

        updated_at = time
        exp_items.append('updatedAt=:ua')
        exp_vals[':ua'] = updated_at

        table = self.get_table()
        res = table.update_item(
            Key={
                'serviceIdSlug': '#'.join([service_id, slug]),
            },
            UpdateExpression='SET ' +  ', '.join(exp_items),
            ExpressionAttributeValues=exp_vals,
            ReturnValues='UPDATED_NEW'
        )
        for attr, val in res['Attributes'].items():
            if attr not in saved:
                continue
            saved[attr] = val

        if cate_slug_upd:
            saved['category'] = cate_upd

        return saved
