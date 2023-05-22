from app.models.dynamodb.base import Base


class Contact(Base):
    table_name = 'contact'
    public_attrs = []
    response_attrs = public_attrs + []
    private_attrs = []
    all_attrs = public_attrs + private_attrs
