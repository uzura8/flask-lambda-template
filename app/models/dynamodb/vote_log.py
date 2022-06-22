from app.models.dynamodb.base import Base


class VoteLog(Base):
    table_name = 'vote-log'
    response_attr = [
    ]
