from boto3.dynamodb.conditions import Key
from app.models.dynamodb import Base, SiteConfig


class Tag(Base):
    table_name = 'tag'
    response_attr = [
        {'key':'tagId', 'label':'tagId'},
        {'key':'serviceId', 'label':'serviceId'},
        {'key':'slug', 'label':'slug'},
        {'key':'label', 'label':'label'},
    ]


    @classmethod
    def get_all_by_service_id(self, service_id):
        return self.get_all_by_pkey({'key':'serviceId', 'val':service_id})
