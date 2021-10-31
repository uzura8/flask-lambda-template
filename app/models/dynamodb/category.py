from boto3.dynamodb.conditions import Key
from app.models.dynamodb import Base, SiteConfig


class Category(Base):
    table_name = 'category'


    @classmethod
    def get_one_by_slug(self, service_id, slug, with_parents=False):
        table = self.get_table()
        res = table.query(
            IndexName='gsi-one-by-slug',
            KeyConditionExpression=Key('serviceIdSlug').eq('#'.join([service_id, slug])),
        )
        if 'Items' not in res or not res['Items']:
            return None

        item = res['Items'][0]
        if not with_parents:
            return item

        parent_ids = item['parentPath'].split('#')
        if len(parent_ids) == 1:
            item['parents'] = []
        else:
            parents = self.get_all_by_ids(parent_ids)
            item['parents'] = parents

        return item


    @classmethod
    def get_all_by_ids(self, ids):
        keys = []
        for cate_id in ids:
            keys.append({'id':int(cate_id)})
        return self.batch_get_items(keys)


    @classmethod
    def get_one_by_id(self, cate_id):
        table = self.get_table()
        res = table.query(
            ProjectionExpression='parentPath',
            KeyConditionExpression=Key('id').eq(cate_id),
        )
        return res['Items'][0] if 'Items' in res and res['Items'] else None


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
            parent_path =  'root'
        else:
            parent = self.get_one_by_id(kwargs['parentId'])
            if parent['parentPath'] == 'root':
                parent_path = str(kwargs['parentId'])
            else:
                parent_path =  '#'.join([parent['parentPath'], str(kwargs['parentId'])])

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
