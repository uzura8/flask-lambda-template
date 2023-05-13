from app.common.date import utc_iso
from app.models.dynamodb.base import Base, ModelInvalidParamsException


class VoteCount(Base):
    table_name = 'vote-count'

    public_attrs = [
        'serviceId',
        'contentId',
        'voteType',
        'voteCount',
        'updatedAt',
    ]
    response_attrs = public_attrs + []
    private_attrs = [
        'contentIdType',
    ]
    all_attrs = public_attrs + private_attrs


    @classmethod
    def update_count(self, service_id, content_id, vote_type):
        table = self.get_table()
        time = utc_iso(False, True)
        table.update_item(
            Key={
                'serviceId': service_id,
                'contentIdType': '#'.join([content_id, vote_type]),
            },
            UpdateExpression="""
                ADD voteCount :incr
                SET updatedAt = :time, contentId = :contId, voteType = :voteType
            """,
            ExpressionAttributeValues={
                ':incr': 1,
                ':time': time,
                ':contId': content_id,
                ':voteType': vote_type,
            }
        )


    @classmethod
    def query_all_by_contentIds(self, service_id, contentIds=None):
        table = self.get_table()
        exp_attr_names = {}
        exp_attr_vals = {}
        key_conds = ['#si = :si']
        option = {}
        exp_attr_names['#si'] = 'serviceId'
        exp_attr_vals[':si'] = service_id

        filter_exp_cids = []
        if contentIds:
            if not isinstance(contentIds, list):
                raise ModelInvalidParamsException('contentIds is must be list type')

            for i, cid in enumerate(contentIds):
                val_name = 'cid' + str(i)
                filter_exp_cids.append('#{v} = :{v}'.format(v=val_name))
                exp_attr_names['#{v}'.format(v=val_name)] = 'contentId'
                exp_attr_vals[':{v}'.format(v=val_name)] = cid

        filter_exp_cids_str = ' OR '.join(filter_exp_cids) if filter_exp_cids else ''

        filter_exp = ''
        if filter_exp_cids_str:
            filter_exp += filter_exp_cids_str

        if filter_exp:
            option['FilterExpression'] = filter_exp

        option['KeyConditionExpression'] = ' AND '.join(key_conds)
        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals
        result = table.query(**option)
        items = result.get('Items', [])

        return items
