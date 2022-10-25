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
