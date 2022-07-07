from app.models.dynamodb.base import Base


class Contact(Base):
    table_name = 'contact'
    response_attr = [
    ]
