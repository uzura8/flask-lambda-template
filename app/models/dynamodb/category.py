from boto3.dynamodb.conditions import Key
from app.models.dynamodb import Base, SiteConfig, Service


class Category(Base):
    table_name = 'category'
    public_attrs = [
        'id',
        'slug',
        'label',
        'serviceId',
        'parentPath',
    ]
    response_attrs = public_attrs + [
        'parents',
        'children',
    ]
    private_attrs = [
        'serviceIdSlug',
    ]
    all_attrs = public_attrs + private_attrs


    @classmethod
    def get_all_by_service_id(self, service_id, is_public=True, is_nested=True):
        table = self.get_table()
        option = {
            'IndexName': 'gsi-list-by-service',
            'ProjectionExpression': self.prj_exps_str(is_public),
            'KeyConditionExpression': '#si = :si',
            'ExpressionAttributeNames': {'#si':'serviceId'},
            'ExpressionAttributeValues': {':si':service_id},
        }
        result = table.query(**option)
        items = result.get('Items')
        if not items:
            return []

        if not is_nested:
            return items

        return self.convert_to_nested(items)


    @classmethod
    def get_one_by_slug(self, service_id, slug, with_parents=False, with_children=False,
                        for_response=False, is_nested=True):
        table = self.get_table()
        res = table.query(
            IndexName='gsi-one-by-slug',
            KeyConditionExpression=Key('serviceIdSlug').eq('#'.join([service_id, slug])),
            ProjectionExpression=self.prj_exps_str(for_response),
        )
        if not res.get('Items'):
            return None

        item = res['Items'][0]

        parent_path = item['parentPath']
        if with_parents:
            parent_ids = parent_path.split('#')
            if len(parent_ids) == 1:
                item['parents'] = []
            else:
                parents = self.get_all_by_ids(parent_ids)
                item['parents'] = parents

            if for_response:
                del item['parentPath']# Removed unnecessary attr

        if with_children:
            if parent_path == '0':
                self_path = str(item['id'])
            else:
                self_path = '%s#%s' % (parent_path, item['id'])
            item['children'] =\
                self.get_children_by_parent_path(service_id, self_path, True,
                                                    for_response, is_nested)

        return self.to_response(item) if for_response else item


    @classmethod
    def get_all_by_ids(self, ids, is_admin=False):
        keys = []
        for cate_id in ids:
            keys.append({'id':int(cate_id)})
        items = self.batch_get_items(keys)
        if is_admin:
            return items

        res = []
        for item in items:
            if item.get('parentPath') == '0':
                continue

            res.append(self.to_response(item))
        return res


    @classmethod
    def get_one_by_id(self, cate_id, is_public=True):
        table = self.get_table()
        res = table.query(
            ProjectionExpression=self.prj_exps_str(is_public),
            KeyConditionExpression=Key('id').eq(cate_id),
        )
        return res['Items'][0] if 'Items' in res and res['Items'] else None


    @classmethod
    def get_children_by_parent_path(self, service_id, parent_path,
                                with_children=False, for_response=False, is_nested=True):
        table = self.get_table()
        option = {
            'IndexName': 'gsi-list-by-service',
            'ProjectionExpression': self.prj_exps_str(for_response),
            'ExpressionAttributeNames': {'#si':'serviceId', '#pp':'parentPath'},
            'ExpressionAttributeValues': {':si':service_id, ':pp':parent_path},
        }
        option['KeyConditionExpression'] = '#si = :si'
        if with_children:
            option['KeyConditionExpression'] += ' AND begins_with(#pp, :pp)'
        else:
            option['KeyConditionExpression'] += ' AND #pp = :pp'

        result = table.query(**option)
        if 'Items' not in result or not result['Items']:
            return []

        res = result['Items']
        if is_nested:
            res = self.convert_to_nested(res, for_response)
        elif for_response:
            res = [ self.to_response(item) for item in res ]

        return res


    @classmethod
    def create(self, vals):
        service_id = vals.get('serviceId')
        if not Service.check_exists(service_id):
            raise ValueError('serviceId is invalid')

        required_attrs = ['slug', 'label']
        for attr in required_attrs:
            if attr not in vals or len(vals[attr].strip()) == 0:
                raise ValueError("Argument '%s' requires values" % attr)

        if vals.get('parentId') is None:
            raise ValueError("Argument 'parentId' requires values")

        if vals['parentId'] == 0:
            parent_path = '0'
        else:
            parent = self.get_one_by_id(vals['parentId'])
            if parent['parentPath'] == '0':
                parent_path = str(vals['parentId'])
            else:
                parent_path = '#'.join([parent['parentPath'], str(vals['parentId'])])

        slug = vals['slug']
        cate_id = SiteConfig.increament_number('category_id')

        table = self.get_table()
        item = {
            'id': cate_id,
            'serviceId': service_id,
            'slug': slug,
            'label': vals['label'],
            'parentPath': parent_path,
            'serviceIdSlug': '#'.join([service_id, slug]),
        }
        table.put_item(Item=item)
        return item


    @classmethod
    def update(self, cate_id, vals, is_check_service_id=False):
        service_id = vals.get('serviceId')
        if is_check_service_id and not Service.check_exists(service_id):
            raise ValueError('serviceId is invalid')

        if vals.get('parentId') is None:
            raise ValueError("Argument 'parentId' requires values")

        if vals['parentId'] == 0:
            parent_path = '0'
        else:
            parent = self.get_one_by_id(vals['parentId'])
            if parent['parentPath'] == '0':
                parent_path = str(vals['parentId'])
            else:
                parent_path = '#'.join([parent['parentPath'], str(vals['parentId'])])

        upd_val = {
            'label': vals['label'],
            'parentPath': parent_path,
        }
        query_keys = {'p': {'key':'id', 'val':cate_id}}
        item = super().update(query_keys, upd_val)
        return item


    @classmethod
    def convert_to_nested(self, categories, for_response=False):
        cates = sorted(categories, key=lambda x: x['parentPath'], reverse=True)
        set_cate_ids = []
        res = {}

        for cate in cates:
            target_key = str(cate['id'])

            # If parent exists at first node of result dict, Added as children
            pid = cate['parentPath'].split('#')[-1]
            if pid in res:
                if 'children' not in res[pid]:
                    res[pid]['children'] = []
                res[pid]['children'].append(self.to_response(cate) if for_response else cate)
                set_cate_ids.append(target_key)
                if target_key in res.keys():
                    res.pop(target_key)
                continue

            # If parent not exists at first node of result dict, Added parent and self
            for item in cates:
                # If already set, skip this
                if item['id'] in set_cate_ids:
                    continue

                # Added to parent as children
                key = str(item['id'])
                if key == pid:
                    if key not in res:
                        res[key] = item
                        res[key]['children'] = []
                    res[key]['children'].append(self.to_response(cate) if for_response else cate)
                    set_cate_ids.append(target_key)
                    if target_key in res.keys():
                        res.pop(target_key)
                    break

        # If nest not exists, return original
        if categories and not res:
            return [ self.to_response(c) if for_response else c for c in categories ]

        return list(res.values())
