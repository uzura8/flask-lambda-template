from boto3.dynamodb.conditions import Key
from app.models.dynamodb import Base, Service
from app.common.date import utc_iso


class ServiceConfig(Base):
    table_name = 'service-config'

    public_attrs = []
    response_attrs = public_attrs + []
    private_attrs = []
    all_attrs = public_attrs + private_attrs


    @classmethod
    def get_val(self, service_id, name):
        item = self.get_one_by_name(service_id, name)
        return item['configVal'] if item else None


    @classmethod
    def get_one_by_name(self, service_id, name):
        table = self.get_table()
        res = table.query(
            KeyConditionExpression=Key('serviceId').eq(service_id) & Key('configName').eq(name)
        )
        return res['Items'][0] if 'Items' in res and res['Items'] else None


    @classmethod
    def save(self, service_id, name, val):
        if not Service.check_exists(service_id):
            raise ValueError('service_id is invalid')

        time = utc_iso(False, True)
        table = self.get_table()
        item = self.get_one_by_name(service_id, name)
        if not item:
            item = {
                'serviceId': service_id,
                'configName': name,
                'configVal': val,
                'updatedAt': time,
            }
            res = table.put_item(Item=item)
            return res

        if item['configVal'] == val:
            return item

        res = table.update_item(
            Key={
                'serviceId': service_id,
                'configName': name,
            },
            AttributeUpdates={
                'configVal': {
                    'Value': val
                },
                'updatedAt': {
                    'Value': time
                }
            },
        )
        return res


    @classmethod
    def increament_number(self, service_id, name):
        if not Service.check_exists(service_id):
            raise ValueError('service_id is invalid')

        item = self.get_one_by_name(service_id, name)
        if not item:
            self.save(service_id, name, 1)
            return 1

        table = self.get_table()
        #service_id_name = '#'.join([service_id, name])
        res = table.update_item(
            Key={
                'serviceId': service_id,
                'configName': name
            },
            UpdateExpression='ADD configVal :incr',
            ExpressionAttributeValues={':incr': 1}
        )
        return self.get_val(service_id, name)
