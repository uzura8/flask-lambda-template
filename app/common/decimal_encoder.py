import json
from decimal import Decimal
from boto3.dynamodb.types import Binary


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            if int(obj) == obj:
                return int(obj)
            return float(obj)
        if isinstance(obj, Binary):
            return obj.value
        if isinstance(obj, bytes):
            return obj.decode()
        if isinstance(obj, set):
            return list(obj)

        try:
            return str(obj)
        except Exception:
            return None
