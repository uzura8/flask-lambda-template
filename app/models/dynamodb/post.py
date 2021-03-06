import mistletoe
from boto3.dynamodb.conditions import Key
from app.common.date import utc_iso, iso_offset2utc
from app.common.string import new_uuid, nl2br, url2link, strip_html_tags
from app.models.dynamodb.base import Base, ModelInvalidParamsException
from app.models.dynamodb.category import Category
from app.models.dynamodb.post_tag import PostTag
from app.models.dynamodb.service import Service


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
        limit = params.get('count', 20)
        cate_slugs = params.get('categories', [])

        is_admin = index_name == 'createdAtGsi'
        sort_key = 'createdAt' if index_name == 'createdAtGsi' else 'publishAt'
        prj_exps = ['title', 'postId', 'slug', 'body', 'bodyText', 'bodyHtml',
                    'publishAt', 'updatedAt', 'categorySlug', 'postStatus', 'createdAt']
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

        if not is_admin:
            status = 'publish'
            current = utc_iso(False, True)
            if not until_time or until_time > current:
                until_time = current

        if status:
            key_conds.append('begins_with(#sp, :sp)')
            exp_attr_names['#sp'] = 'statusPublishAt'
            exp_attr_vals[':sp'] = status

        filter_exps = []
        if since_time:
            cond = '#st > :st'
            exp_attr_names['#st'] = sort_key
            exp_attr_vals[':st'] = since_time
            if is_admin:
                key_conds.append(cond)
            else:
                filter_exps.append(cond)

        if until_time:
            cond = '#ut < :ut'
            exp_attr_names['#ut'] = sort_key
            exp_attr_vals[':ut'] = until_time
            if is_admin:
                key_conds.append(cond)
            else:
                filter_exps.append(cond)

        filter_exp_cids = []
        if cate_slugs:
            for i, cid in enumerate(cate_slugs):
                val_name = 'cid' + str(i)
                filter_exp_cids.append('#{v} = :{v}'.format(v=val_name))
                exp_attr_names['#{v}'.format(v=val_name)] = 'categorySlug'
                exp_attr_vals[':{v}'.format(v=val_name)] = cid

        filter_exps_str = ' AND '.join(filter_exps) if filter_exps else ''
        filter_exp_cids_str = '(%s)' % ' OR '.join(filter_exp_cids) if filter_exp_cids else ''

        filter_exp = ''
        if filter_exps_str:
            filter_exp += filter_exps_str
        if filter_exp_cids_str:
            if filter_exp:
                filter_exp += ' AND '
            filter_exp += filter_exp_cids_str

        if filter_exp:
            option['FilterExpression'] = filter_exp
            option['Limit'] += 50

        option['KeyConditionExpression'] = ' AND '.join(key_conds)
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


    @classmethod
    def query_pager(self, hkey, params=None, with_cate=False):
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

        key_cond_exps.append('#hk = :hv')
        exp_attr_names['#hk'] = hkey['name']
        exp_attr_vals[':hv'] = hkey['value']

        option['KeyConditionExpression'] = ' AND '.join(key_cond_exps)
        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals

        if start_key:
            option['ExclusiveStartKey'] = start_key

        res = table.query(**option)
        items = res['Items']

        if with_cate:
            for idx, item in enumerate(items):
                cate = Category.get_one_by_slug(hkey['value'], item['categorySlug'],
                                                            False, False, True)
                items[idx]['category'] = cate

        return {
            'items': items,
            'lastKey': res['LastEvaluatedKey'] if 'LastEvaluatedKey' in res else None,
        }


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
    def get_one_by_id(self, post_id, with_relations=False, for_response=True):
        item = self.get_one_by_pkey('postId', post_id)
        if not item:
            return None

        if with_relations:
            if item.get('categorySlug'):
                item['category'] = Category.get_one_by_slug(item['serviceId'],
                                        item['categorySlug'], True, False, True)
            item['tags'] = PostTag.get_all_by_post_id(post_id, True, for_response)

        return item


    @classmethod
    def query_all_by_tag_id(self, tag_id, params):
        items = PostTag.query_all_by_tag_id(tag_id, params)
        if not items:
            return []

        keys = [ {'postId':d['postId']} for d in items ]
        posts = Post.batch_get_items(keys)
        is_desc = params.get('order', 'asc') == 'desc'
        sort_key = 'publishAt'
        return sorted(posts, key=lambda x: x[sort_key], reverse=is_desc)


    @classmethod
    def get_one_by_slug(self, service_id, slug, with_cate=False, for_response=True):
        item = self.get_one_by_pkey('serviceIdSlug', '#'.join([service_id, slug]), True, 'serviceIdSlugGsi')
        if not item:
            return None

        if with_cate and item.get('categorySlug'):
            if item.get('categorySlug'):
                item['category'] = Category.get_one_by_slug(service_id,
                                    item['categorySlug'], True, False, True)
            item['tags'] = PostTag.get_all_by_post_id(item['postId'], True, for_response)

        return item


    @classmethod
    def create(self, vals):
        service_id = vals.get('serviceId')
        if not service_id:
            raise ModelInvalidParamsException('serviceId is required')

        if not Service.check_exists(service_id):
            raise ModelInvalidParamsException('serviceId not exists')

        item = Post.get_one_by_slug(service_id, vals['slug'])
        if item:
            raise ModelInvalidParamsException('Slug already used')

        if vals.get('category'):
            cate = Category.get_one_by_slug(service_id, vals['category'])
            if not cate:
                raise ModelInvalidParamsException('Category not exists')

        status = vals.get('status') or vals.get('postStatus')
        if status not in ['publish', 'unpublish']:
            raise ModelInvalidParamsException('status is invalid')
        is_publish = status == 'publish'

        time = utc_iso(False, True)

        publish_at = ''
        if vals.get('publishAt'):
            publish_at = iso_offset2utc(vals['publishAt'], True)
        elif is_publish:
            publish_at = time

        required_attrs = ['slug', 'title']
        for attr in required_attrs:
            if attr not in vals or len(vals[attr].strip()) == 0:
                raise ModelInvalidParamsException("Argument '%s' requires values" % attr)

        slug = vals['slug']
        cate_slug = vals['category']

        body_raw = vals['body']
        body_format = vals['bodyFormat']
        body_html, body_text = self.conv_body_to_each_format(body_raw, body_format)

        table = self.get_table()
        item = {
            'postId': new_uuid(),
            'createdAt': time,
            'createdBy': vals.get('createdBy'),
            #'updatedAt': time,
            'serviceId': service_id,
            'slug': slug,
            'publishAt': publish_at,
            'categorySlug': cate_slug,
            'title': vals['title'],
            'body': body_raw,
            'bodyHtml': body_html,
            'bodyText': body_text,
            'bodyFormat': body_format,
            'serviceIdSlug': '#'.join([service_id, slug]),
            'postStatus': status,
            'statusPublishAt': '#'.join([status, publish_at]),
        }
        table.put_item(Item=item)
        return item


    @classmethod
    def update(self, post_id, vals):
        time = utc_iso(False, True)
        saved = self.get_one_by_pkey('postId', post_id, True)
        if not saved:
            raise ModelInvalidParamsException('postId is invalid')

        service_id = saved['serviceId']

        slug_upd = vals.get('slug')
        if slug_upd and slug_upd != saved['slug']:
            if Post.get_one_by_slug(service_id, slug_upd):
                raise ModelInvalidParamsException('Slug already used')
        else:
            slug_upd = None

        cate_slug_upd = vals.get('category')
        if cate_slug_upd and cate_slug_upd != saved['categorySlug']:
            cate_upd = Category.get_one_by_slug(service_id, cate_slug_upd)
            if not cate_upd:
                raise ModelInvalidParamsException('Category not exists', 400)
        else:
            cate_slug_upd = None

        status_upd = vals.get('status')
        if status_upd:
            if status_upd not in ['publish', 'unpublish']:
                raise ModelInvalidParamsException('status is invalid')

            if status_upd == saved['postStatus']:
                status_upd = None

        is_published = status_upd and status_upd == 'publish'

        publish_at_upd = vals.get('publishAt', '')
        if publish_at_upd:
            if publish_at_upd != saved['publishAt']:
                publish_at_upd = iso_offset2utc(vals['publishAt'], True)
        else:
            if is_published and not saved['publishAt']:
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

        if publish_at_upd:
            exp_items.append('publishAt=:pa')
            exp_vals[':pa'] = publish_at_upd

        if status_upd or publish_at_upd:
            exp_items.append('statusPublishAt=:spa')
            join_item = status_upd if status_upd else saved['postStatus']
            publish_at = publish_at_upd if publish_at_upd else saved['publishAt']
            exp_vals[':spa'] = '#'.join([join_item, publish_at])

        attrs = ['title', 'body', 'bodyFormat', 'updatedBy']
        upd_attrs = []
        for attr in attrs:
            val = vals.get(attr)
            if val is None or val == saved.get(attr):
                continue

            exp_items.append('%s=:%s' % (attr, attr))
            exp_vals[':' + attr] = val
            upd_attrs.append(attr)

        if not exp_items:
            return

        if 'body' in upd_attrs or 'bodyFormat' in upd_attrs:
            body_html, body_text = self.conv_body_to_each_format(vals['body'], vals['bodyFormat'])
            exp_items.append('%s=:%s' % ('bodyHtml', 'bodyHtml'))
            exp_items.append('%s=:%s' % ('bodyText', 'bodyText'))
            exp_vals[':bodyHtml'] = body_html
            exp_vals[':bodyText'] = body_text

        updated_at = time
        exp_items.append('updatedAt=:ua')
        exp_vals[':ua'] = updated_at

        table = self.get_table()
        res = table.update_item(
            Key={
                'postId': post_id,
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
        else:
            saved['category'] = Category.get_one_by_slug(service_id, saved['categorySlug'],
                                                        True, False, True)

        return saved

    @staticmethod
    def conv_body_to_each_format(body_raw, body_format):
        body_html = ''
        body_text = ''
        if body_format == 'markdown':
            body_html = mistletoe.markdown(body_raw)
            body_text = strip_html_tags(body_html)
        elif body_format == 'text':
            body_html = nl2br(url2link(body_raw))
            body_text = body_raw
        else:
            body_html = body_raw
            body_text = strip_html_tags(body_raw)
        return body_html, body_text
