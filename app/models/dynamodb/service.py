from boto3.dynamodb.conditions import Key
from app.models.dynamodb import Base


class Service(Base):
    table_name = 'service'
    response_attr = [
    ]
