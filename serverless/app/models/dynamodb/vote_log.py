from app.models.dynamodb.base import Base


class VoteLog(Base):
    table_name = 'vote-log'

    public_attrs = []
    response_attrs = public_attrs + []
    private_attrs = []
    all_attrs = public_attrs + private_attrs
