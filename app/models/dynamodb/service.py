from boto3.dynamodb.conditions import Key
from app.models.dynamodb import Base


class Service(Base):
    table_name = 'service'
    response_attrs = [
    ]


    @classmethod
    def check_exists(self, service_id):
        item = self.get_one({'p': {'key':'serviceId', 'val':service_id}})
        return bool(item)
