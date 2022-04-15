from boto3.dynamodb.conditions import Key
from app.models.dynamodb import Base
from app.models.dynamodb.tag import Tag


class PostTag(Base):
    table_name = 'post-tag'
    response_attr = [
        {'key':'postId', 'label':'postId'},
        {'key':'tagId', 'label':'tagId'},
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
