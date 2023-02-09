from boto3.dynamodb.conditions import Key
from app.common.date import utc_iso
from app.models.dynamodb.base import Base


class PostGroup(Base):
    table_name = 'post-group'
    public_attrs = [
        'serviceId',
        'slug',
        'label',
        'postIds',
        'createdAt',
        'updatedAt',
    ]
    response_attrs = public_attrs + [
        'posts',
    ]
    private_attrs = [
        'serviceIdSlug',
    ]
    all_attrs = public_attrs + private_attrs

    reserved_values = {
        'slug': ['slug', 'create']
    }


    @classmethod
    def delete_post_id_for_all_items(self, service_id, post_id):
        pkeys = {'key':'serviceId', 'val':service_id}
        groups = PostGroup.get_all_by_pkey(pkeys, None, 'PostGroupsByServiceIdGsi')
        if not groups:
            return []

        upd_pkeys = []
        for group in groups:
            if post_id not in group.get('postIds', []):
                continue

            group['postIds'].remove(post_id)
            query_key = '#'.join([service_id, group['slug']])
            query_keys = {'p': {'key':'serviceIdSlug', 'val':query_key}}
            vals = {'postIds':group['postIds']}
            PostGroup.update(query_keys, vals)
            upd_pkeys.append(query_key)

        return upd_pkeys
