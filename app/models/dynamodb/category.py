from boto3.dynamodb.conditions import Key
from app.models.dynamodb import Base, SiteConfig


class Category(Base):
    table_name = 'category'
    response_attr = [
        {'key':'id', 'label':'id'},
        {'key':'slug', 'label':'slug'},
        {'key':'label', 'label':'label'},
    ]


    @classmethod
    def get_one_by_slug(self, service_id, slug, with_parents=False, with_children=False):
        table = self.get_table()
        res = table.query(
            IndexName='gsi-one-by-slug',
            KeyConditionExpression=Key('serviceIdSlug').eq('#'.join([service_id, slug])),
            ProjectionExpression='id, slug, label, parentPath',
        )
        if 'Items' not in res or not res['Items']:
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

            del item['parentPath']# Removed unnecessary attr

        if with_children:
            self_path = '{}#{}'.format(parent_path, item['id'])
            item['children'] = self.get_children_by_parent_path(service_id, self_path)

        return item


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
            if item.get('parentPath') == 'root':
                continue

            res.append(self.to_response(item))
        return res


    @classmethod
    def get_one_by_id(self, cate_id):
        table = self.get_table()
        res = table.query(
            ProjectionExpression='slug, label, parentPath',
            KeyConditionExpression=Key('id').eq(cate_id),
        )
        return res['Items'][0] if 'Items' in res and res['Items'] else None


    @classmethod
    def get_children_by_parent_path(self, service_id, parent_path):
        table = self.get_table()
        option = {
            'IndexName': 'gsi-list-by-service',
            'ProjectionExpression': 'slug',
            'KeyConditionExpression': '#si = :si AND begins_with(#pp, :pp)',
            'ExpressionAttributeNames': {'#si':'serviceId', '#pp':'parentPath'},
            'ExpressionAttributeValues': {':si':service_id, ':pp':parent_path},
        }
        result = table.query(**option)
        if 'Items' not in result or not result['Items']:
            return []

        res = []
        for item in result['Items']:
            res.append(self.to_response(item))

        return res


    @classmethod
    def create(self, service_id, kwargs):
        if service_id not in self.ACCEPT_SERVICE_IDS:
            raise ValueError('service_id is invalid')

        required_attrs = ['slug', 'label']
        for attr in required_attrs:
            if attr not in kwargs or len(kwargs[attr].strip()) == 0:
                raise ValueError("Argument '%s' requires values" % attr)

        if 'parentId' not in kwargs or kwargs['parentId'] is None:
            raise ValueError("Argument 'parentId' requires values")

        if kwargs['parentId'] == 0:
            parent_path = 'root'
        else:
            parent = self.get_one_by_id(kwargs['parentId'])
            if parent['parentPath'] == 'root':
                parent_path = str(kwargs['parentId'])
            else:
                parent_path = '#'.join([parent['parentPath'], str(kwargs['parentId'])])

        slug = kwargs['slug']
        cate_id = SiteConfig.increament_number(service_id, 'category_id')

        table = self.get_table()
        item = {
            'id': cate_id,
            'serviceId': service_id,
            'slug': slug,
            'label': kwargs['label'],
            'parentPath': parent_path,
            'serviceIdSlug': '#'.join([service_id, slug]),
        }
        table.put_item(Item=item)
        return item
