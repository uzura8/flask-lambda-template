from app.models.dynamodb.base import Base


class ShortenUrlDomain(Base):
    table_name = 'shorten-url-domain'
    public_attrs = [
        'domain',
        'createdAt',
        'updatedAt',
    ]
    response_attrs = public_attrs + []
    private_attrs = [
        'serviceIdDomain',
        'serviceId',
        'createdBy',
    ]
    all_attrs = public_attrs + private_attrs
