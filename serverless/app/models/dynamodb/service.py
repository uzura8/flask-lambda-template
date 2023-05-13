from boto3.dynamodb.conditions import Key
from app.models.dynamodb import Base


class Service(Base):
    table_name = 'service'

    public_attrs = [
        'serviceId',
        'label',
        'functions',
        'configs'
    ]
    response_attrs = public_attrs + []
    private_attrs = [
        'createdAt',
    ]
    all_attrs = public_attrs + private_attrs

    allowed_functions = ['post', 'urlShortener']

    @classmethod
    def get_one_by_id(self, service_id):
        return self.get_one({'p': {'key':'serviceId', 'val':service_id}})


    @classmethod
    def check_exists(self, service_id):
        item = self.get_one_by_id(service_id)
        return bool(item)
