from boto3.dynamodb.conditions import Key
from app.models.dynamodb import Base


class Tag(Base):
    table_name = 'tag'
    response_attr = [
        {'key':'tagId', 'label':'tagId'},
        #{'key':'serviceId', 'label':'serviceId'},
        {'key':'label', 'label':'label'},
    ]


    @classmethod
    def get_all_by_service_id(self, service_id, params=None, for_response=True):
        table = self.get_table()

        is_asc = True
        limit = 50
        if params:
            is_asc = params.get('order', 'asc') == 'asc'
            limit = params.get('count', 50)

        res = table.query(
            IndexName='TagsByServiceIdGsi',
            KeyConditionExpression=Key('serviceId').eq(service_id),
            ScanIndexForward=is_asc,
            Limit=limit
        )
        items = res.get('Items', [])
        return [ self.to_response(i) for i in items ] if for_response else items
